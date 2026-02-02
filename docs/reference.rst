``kusto_tool`` API reference
============================

Core entry points
-----------------

The primary entry points are:

- ``q("Table")`` to start a query with no schema context.
- ``col("Column")`` to build expressions without a schema.
- ``TableExpr`` methods like ``project``, ``where``, and ``summarize``.

Function helpers
----------------

The :mod:`kusto_tool.function` module provides common KQL function wrappers
that return expression objects. These objects can be passed into
``summarize`` or ``extend`` without requiring schema inspection.

.. automodule:: kusto_tool.database
   :members:

.. automodule:: kusto_tool.expression
   :members:

.. automodule:: kusto_tool.function
   :members:
