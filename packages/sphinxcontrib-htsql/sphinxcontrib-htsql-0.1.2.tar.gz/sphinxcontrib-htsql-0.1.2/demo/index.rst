HTSQL Demo
==========

This document demonstrates different options of the ``htsql`` directive.

Simple query
------------

The ``htsql`` directive takes a query as a parameter.

.. sourcecode:: rst

   .. htsql:: /school?campus='old'

.. htsql:: /school?campus='old'

Multiline query
---------------

If a query spans many lines, it could be written within the directive body.

.. sourcecode:: rst

   .. htsql::

      /school.define(num_dept := count(department))
             {code, num_dept}?num_dept>3

.. htsql::

   /school.define(num_dept := count(department))
          {code, num_dept}?num_dept>3

Custom output
-------------

If you want to display one query with the output of another query, use
``output`` option.  It is useful for describing destructive operations,
not-yet-implemented features or escaping rules.  You need to quote
whitespace and special characters manually.

.. sourcecode:: rst

   .. htsql:: /school?campus='north'
      :output: /school?campus='south'

.. htsql:: /school?campus='north'
   :output: /school?campus='south'

Errors
------

Normally, the ``htsql`` directive expects the query to be valid.  Use ``error``
option to indicate that the query is invalid and you want to show the error
message.

.. sourcecode:: rst

   .. htsql:: /school{code, title}
      :error:

.. htsql:: /school{code, title}
   :error:

Disable linking
---------------

Normally, the query is rendered with a link leading to the HTSQL service.  Use
``no-link`` option to disable this feature.

.. sourcecode:: rst

   .. htsql:: /school?exists(department)
      :no-link:

.. htsql:: /school?exists(department)
   :no-link:

Hiding query output
-------------------

Use ``no-output`` option to render the query, but not the output.

.. sourcecode:: rst

   .. htsql:: /school[ns]
      :no-output:

.. htsql:: /school[ns]
   :no-output:

Hiding query
------------

Use ``no-input`` option to render the query output, but not the query itself.

.. sourcecode:: rst

   .. htsql:: /school[ns]
      :no-input:

.. htsql:: /school[ns]
   :no-input:

Raw output
----------

Normally, query output is rendered as a table.  Use option ``raw`` to render
the output unformatted.

.. sourcecode:: rst

   .. htsql:: /school[ns]/:json
      :raw:

.. htsql:: /school[ns]/:json
   :raw:

Truncating output
-----------------

Use ``cut`` option to truncate the query output up to the given number
of lines.  This option works both with tabular and raw output.

.. sourcecode:: rst

   .. htsql:: /school
      :cut: 3

.. htsql:: /school
   :cut: 3

