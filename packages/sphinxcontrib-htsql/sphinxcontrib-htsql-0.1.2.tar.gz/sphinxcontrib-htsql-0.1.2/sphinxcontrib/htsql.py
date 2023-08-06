#
# Copyright (c) 2013, Prometheus Research, LLC
#


from __future__ import unicode_literals

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util.osutil import copyfile
from pygments.lexer import RegexLexer
from pygments.token import (Punctuation, Text, Operator, Name, String, Number,
        Comment)

import sys
import re
import os, os.path
from cgi import escape
from json import loads

is_py3 = (sys.version_info >= (3,))

if not is_py3:
    from urllib2 import quote, urlopen, Request, HTTPError, URLError
else:
    from urllib.parse import quote
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

try:
    unicode
except NameError:
    unicode = str


class HtsqlLexer(RegexLexer):

    name = 'HTSQL'
    aliases = ['htsql']
    filenames = ['*.htsql']
    mimetypes = ['text/x-htsql', 'application/x-htsql']

    ascii_escape_regexp = re.compile(r'%(?P<code>[0-7][0-9A-Fa-f])')

    tokens = {
        str('root'): [
            (r'\s+', Text),
            (r'\#[^\r\n]*', Comment.Single),
            (r'\'(?:[^\']|\'\')*\'', String),
            (r'(?:\d+(?:\.\d*)?|\.\d+)[eE][+-]?\d+', Number),
            (r'\d+\.\d*|\.\d+', Number),
            (r'\d+', Number),
            (r'(?<=:)\w+', Name.Function),
            (r'\w+(?=\s*\()', Name.Function),
            (r'\w+', Name.Builtin),
            (r'~|!~|<=|<|>=|>|==|=|!==|!=|'
             r'\^|\?|->|@|:=|!|&|\||\+|-|\*|/', Operator),
            (r'\(|\)|\{|\}|\.|,|:|;|\$', Punctuation),
            (r'\[', Punctuation, str('identity')),
        ],
        str('identity'): [
            (r'\s+', Text),
            (r'\(|\[', Punctuation, str('#push')),
            (r'\)|\]', Punctuation, str('#pop')),
            (r'\.', Punctuation),
            (r'[\w-]+', String),
            (r'\'(?:[^\']|\'\')*\'', String),
            (r'\$', Punctuation, str('name')),
        ],
        str('name'): [
            (r'\s+', Text),
            (r'\w+', Name.Builtin, str('#pop')),
        ],
    }

    def get_tokens_unprocessed(self, text):
        quotes = []
        groups = []
        for match in self.ascii_escape_regexp.finditer(text):
            quotes.append(match.start())
            groups.append(match.group())
        text = self.ascii_escape_regexp.sub(
                lambda m: chr(int(m.group('code'), 16)), text)
        token_stream = super(HtsqlLexer, self).get_tokens_unprocessed(text)
        pos_inc = 0
        for pos, token, value in token_stream:
            pos += pos_inc
            while quotes and pos <= quotes[0] < pos+len(value):
                idx = quotes.pop(0)-pos
                repl = groups.pop(0)
                value = value[:idx]+repl+value[idx+1:]
                pos_inc += len(repl)-1
            yield (pos, token, value)


class HTSQLRootDirective(Directive):

    required_arguments = 1
    has_content = False

    def run(self):
        env = self.state.document.settings.env
        env.htsql_root = self.arguments[0]
        return []


class HTSQLDirective(Directive):

    optional_arguments = 1
    has_content = True
    final_argument_whitespace = True
    option_spec = {
            'output': directives.path,
            'error': directives.flag,
            'no-link': directives.flag,
            'no-input': directives.flag,
            'no-output': directives.flag,
            'raw': directives.flag,
            'cut': directives.positive_int,
    }

    def run(self):
        doc = self.state.document
        env = doc.settings.env
        if self.arguments:
            if self.content:
                return [doc.reporter.error("htsql directive cannot have both"
                                           " an argument and a body",
                                           lineno=self.lineno)]
            query  = " ".join(line.strip()
                              for line in self.arguments[0].split("\n"))
        elif self.content:
            query = "\n".join(self.content).strip()
        else:
            return [doc.reporter.error("htsql directive expects an argument"
                                       " or a body", lineno=self.lineno)]
        query_node = htsql_block(query, query)
        query_node['language'] = 'htsql'
        if not hasattr(env, 'htsql_root') or not env.htsql_root:
            return [doc.reporter.error("config option `htsql_root`"
                                       " is not set", lineno=self.lineno)]
        if not is_py3:
            if 'output' not in self.options:
                query = quote(query.encode('utf-8'),
                              safe=str("~`!@$^&*()={[}]|:;\"'<,>?/"))
            else:
                query = self.options['output'].encode('utf-8')
        else:
            if 'output' not in self.options:
                query = quote(query,
                              safe="~`!@$^&*()={[}]|:;\"'<,>?/")
            else:
                query = self.options['output']
        uri = env.htsql_root+query
        if 'no-link' not in self.options:
            query_node['uri'] = uri
        if not hasattr(env, 'htsql_uris'):
            env.htsql_uris = {}
        if uri not in env.htsql_uris:
            result = load_uri(uri, 'error' in self.options)
            if not result:
                return [doc.reporter.error("failed to execute an HTSQL query:"
                                           " %s" % uri, line=self.lineno)]
            env.htsql_uris[uri] = result
        htsql_container = nodes.container(classes=['htsql-io'])
        if 'no-input' not in self.options:
            query_container = nodes.container('', query_node,
                                              classes=['htsql-input'])
            htsql_container += query_container
        if 'no-output' in self.options:
            return [htsql_container]
        content_type, content = env.htsql_uris[uri]
        if 'raw' in self.options:
            content_type = 'text/plain'
        result_node = build_result(self.content_offset, content_type, content,
                                   self.options.get('cut'))
        result_container = nodes.container('', result_node,
                                           classes=['htsql-output'])
        htsql_container += result_container
        return [htsql_container]


class htsql_block(nodes.literal_block):
    pass


def visit_htsql_block(self, node):
    # Adapted from `visit_literal_block()`
    if node.rawsource != node.astext():
        return self.visit_literal_block(self, node)
    lang = self.highlightlang
    linenos = node.rawsource.count('\n') >= \
              self.highlightlinenothreshold - 1
    highlight_args = node.get('highlight_args', {})
    if node.has_key('language'):
        lang = node['language']
        highlight_args['force'] = True
    if node.has_key('linenos'):
        linenos = node['linenos']
    highlight_args['nowrap'] = True
    def warner(msg):
        self.builder.warn(msg, (self.builder.current_docname, node.line))
    highlighted = self.highlighter.highlight_block(
        node.rawsource, lang, warn=warner, linenos=linenos,
        **highlight_args)
    if node.has_key('uri'):
        highlighted = '<a href="%s" target="_new" class="htsql-link">%s</a>' \
                % (escape(node['uri'], True), highlighted)
        highlighted = '<a href="%s" target="_new" class="htsql-arrow-link"></a>%s' \
                % (escape(node['uri'], True), highlighted)
    highlighted = '<pre>%s</pre>' % highlighted
    highlighted = '<div class="highlight">%s</div>' % highlighted
    starttag = self.starttag(node, 'div', suffix='',
                             CLASS='highlight-%s' % lang)
    self.body.append(starttag + highlighted + '</div>\n')
    raise nodes.SkipNode


def depart_htsql_block(self, node):
    self.depart_literal_block(node)


def purge_htsql_root(app, env, docname):
    if hasattr(env, 'htsql_root'):
        del env.htsql_root
    if env.config.htsql_root:
        env.htsql_root = env.config.htsql_root


def copy_static(app, exception):
    if app.builder.name != 'html' or exception:
        return
    src = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'htsql.css')
    dst = os.path.join(app.builder.outdir, '_static', 'htsql.css')
    copyfile(src, dst)


def load_uri(uri, error=False):
    try:
        headers = { 'Accept': 'x-htsql/raw' }
        request = Request(uri, headers=headers)
        response = urlopen(request)
        info = response.info()
        if hasattr(info, 'get_content_type'):
            content_type = info.get_content_type()
        else:
            content_type = info.gettype()
        content = response.read()
    except HTTPError as response:
        if not error:
            return None
        info = response.info()
        if hasattr(info, 'get_content_type'):
            content_type = info.get_content_type()
        else:
            content_type = info.gettype()
        content = response.read()
    except URLError:
        return None
    return (content_type, content)


def build_result(line, content_type, content, cut=None):
    content = content.decode('utf-8', 'replace')
    if content_type == 'application/javascript':
        product = loads(content)
        if isinstance(product, dict) and 'meta' in product:
            return build_result_table(product, cut)
    if cut and content.count('\n') > cut:
        start = 0
        while cut:
            start = content.find('\n', start)+1
            cut -= 1
        content = content[:start]+"\u2026\n"
    result_node = nodes.literal_block(content, content)
    result_node['language'] = 'text'
    return result_node


def build_result_table(product, cut):
    meta = product.get('meta')
    data = product.get('data')
    if 'domain' not in meta:
        return
    build = get_build_by_domain(meta['domain'])
    if not build.span:
        return
    table_node = nodes.table()
    measures = build.measures(data, cut)
    group_node = nodes.tgroup(cols=build.span)
    table_node += group_node
    for measure in measures:
        colspec_node = nodes.colspec(colwidth=measure)
        group_node += colspec_node
    head_node = nodes.thead()
    group_node += head_node
    head_rows = build.head(build.head_height())
    if head_rows:
        for row in head_rows:
            row_node = nodes.row()
            head_node += row_node
            for cell, rowspan, colspan, classes in row:
                entry_node = nodes.entry(classes=classes)
                if rowspan > 1:
                    entry_node['morerows'] = rowspan-1
                if colspan > 1:
                    entry_node['morecols'] = colspan-1
                row_node += entry_node
                para_node = nodes.paragraph()
                entry_node += para_node
                text_node = nodes.Text(cell)
                para_node += text_node
                #entry_node += text_node
    body_node = nodes.tbody()
    group_node += body_node
    body_rows = build.body(build.body_height(data, cut), data, cut)
    if body_rows:
        for row in body_rows:
            row_node = nodes.row()
            body_node += row_node
            for cell, rowspan, colspan, classes in row:
                entry_node = nodes.entry(classes=classes)
                if rowspan > 1:
                    entry_node['morerows'] = rowspan-1
                if colspan > 1:
                    entry_node['morecols'] = colspan-1
                row_node += entry_node
                para_node = nodes.paragraph()
                entry_node += para_node
                text_node = nodes.Text(cell)
                para_node += text_node
                #entry_node += text_node
    return table_node


def get_build_by_domain(domain):
    if domain['type'] == 'list':
        return ListBuild(domain)
    elif domain['type'] == 'record':
        return RecordBuild(domain)
    else:
        return ScalarBuild(domain)


class MetaBuild(object):

    def __init__(self, profile):
        self.profile = profile
        self.header = profile.get('header')
        if not self.header:
            self.header = ""
        self.domain_build = get_build_by_domain(profile['domain'])
        self.span = self.domain_build.span

    def head_height(self):
        if not self.span:
            return 0
        height = self.domain_build.head_height()
        if self.header:
            height += 1
        return height

    def head(self, height):
        rows = [[] for idx in range(height)]
        if not self.span or not height:
            return rows
        is_last = (not self.domain_build.head_height())
        if not is_last:
            rows = [[]] + self.domain_build.head(height-1)
        rowspan = 1
        if is_last:
            rowspan = height
        colspan = self.span
        classes = []
        if not self.header:
            classes.append('htsql-dummy')
        rows[0].append((self.header.replace(" ", "\xA0"),
                        rowspan, colspan, classes))
        return rows

    def body_height(self, data, cut):
        return self.domain_build.body_height(data, cut)

    def body(self, height, data, cut):
        return self.domain_build.body(height, data, cut)

    def cut(self, height):
        return self.domain_build.cut(height)

    def measures(self, data, cut):
        measures = self.domain_build.measures(data, cut)
        if len(measures) == 1:
            measures[0] = max(measures[0], len(self.header))
        return measures


class ListBuild(object):

    def __init__(self, domain):
        self.item_build = get_build_by_domain(domain['item']['domain'])
        self.span = self.item_build.span

    def head_height(self):
        if not self.span:
            return []
        return self.item_build.head_height()

    def head(self, height):
        if not self.span or not height:
            return [[] for idx in range(height)]
        return self.item_build.head(height)

    def body_height(self, data, cut):
        if not self.span or not data:
            return 0
        height = 0
        for item in data:
            item_height = self.item_build.body_height(item, None)
            if cut and height+item_height > cut:
                return height+1
            height += item_height
        return height

    def body(self, height, data, cut):
        if not self.span or not height:
            return [[] for idx in range(height)]
        if not data:
            rows = [[] for idx in range(height)]
            rows[0].append(("", height, self.span, ['htsql-dummy']))
            return rows
        rows = []
        for idx, item in enumerate(data):
            item_height = self.item_build.body_height(item, None)
            if cut and len(rows)+item_height > cut:
                rows += self.item_build.cut(height)
                break
            if idx == len(data)-1 and item_height < height:
                item_height = height
            height -= item_height
            rows += self.item_build.body(item_height, item, None)
        return rows

    def cut(self, height):
        if not self.span or not height:
            return [[] for idx in range(height)]
        return self.item_build.cut(height)

    def measures(self, data, cut):
        measures = [1 for idx in range(self.span)]
        if not self.span or not data:
            return measures
        height = 0
        for idx, item in enumerate(data):
            height += self.item_build.body_height(item, None)
            if cut and height > cut:
                break
            item_measures = self.item_build.measures(item, None)
            measures = [max(measure, item_measure)
                        for measure, item_measure
                            in zip(measures, item_measures)]
        return measures


class RecordBuild(object):

    def __init__(self, domain):
        self.field_builds = [MetaBuild(field) for field in domain['fields']]
        self.span = sum(field_build.span for field_build in self.field_builds)

    def head_height(self):
        if not self.span:
            return 0
        return max(field_build.head_height()
                   for field_build in self.field_builds)

    def head(self, height):
        rows = [[] for idx in range(height)]
        if not self.span or not height:
            return rows
        for field_build in self.field_builds:
            field_rows = field_build.head(height)
            rows = [row+field_row
                    for row, field_row in zip(rows, field_rows)]
        return rows

    def body_height(self, data, cut):
        if not self.span:
            return 0
        if not data:
            data = [None]*len(self.field_builds)
        return max(field_build.body_height(item, cut)
                   for field_build, item in zip(self.field_builds, data))

    def body(self, height, data, cut):
        rows = [[] for idx in range(height)]
        if not self.span:
            return rows
        if not data:
            data = [None]*len(self.field_builds)
        for field_build, item in zip(self.field_builds, data):
            field_rows = field_build.body(height, item, cut)
            rows = [row+field_row
                    for row, field_row in zip(rows, field_rows)]
        return rows

    def cut(self, height):
        rows = [[] for idx in range(height)]
        if not self.span or not height:
            return rows
        for field_build in self.field_builds:
            field_rows = field_build.cut(height)
            rows = [row+field_row
                    for row, field_row in zip(rows, field_rows)]
        return rows

    def measures(self, data, cut):
        if not data:
            data = [None]*self.span
        measures = []
        for field_build, item in zip(self.field_builds, data):
            measures += field_build.measures(item, cut)
        return measures


class ScalarBuild(object):

    def __init__(self, domain):
        self.domain = domain
        self.span = 1

    def head_height(self):
        return 0

    def head(self, height):
        rows = [[] for idx in range(height)]
        if not height:
            return rows
        rows[0].append(("", height, 1, ['htsql-dummy']))
        return rows

    def body_height(self, data, cut):
        return 1

    def body(self, height, data, cut):
        rows = [[] for idx in range(height)]
        if not height:
            return rows
        classes = ['htsql-%s-type' % self.domain['type']]
        if data is None:
            classes.append('htsql-null-val')
            data = ""
        elif data is True:
            classes.append('htsql-true-val')
            data = "true"
        elif data is False:
            classes.append('htsql-false-val')
            data = "false"
        else:
            data = unicode(data)
            if not data:
                classes.append('htsql-empty-val')
        rows[0].append((data, height, 1, classes))
        return rows

    def cut(self, height):
        rows = [[] for idx in range(height)]
        if not height:
            return rows
        classes = ['htsql-%s-type' % self.domain['type'], 'htsql-cut']
        rows[0].append(("", height, 1, classes))
        return rows

    def measures(self, data, cut):
        if data is None:
            return [1]
        return [max(1, len(unicode(data)))]


def setup(app):
    app.add_config_value('htsql_root', None, 'env')
    app.add_directive('htsql-root', HTSQLRootDirective)
    app.add_directive('htsql', HTSQLDirective)
    app.connect(str('env-purge-doc'), purge_htsql_root)
    app.connect(str('build-finished'), copy_static)
    app.add_node(htsql_block,
                 html=(visit_htsql_block, depart_htsql_block))
    app.add_stylesheet('htsql.css')
    app.add_lexer('htsql', HtsqlLexer())


