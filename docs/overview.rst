Overview of `kusto-tool`
========================

`kusto-tool` is a Python package providing a high-level interface for generating
Kusto query text. It does not connect to Azure Data Explorer; it only builds
KQL strings.

This package is an experimental work-in-progress and the API is unstable.
Expect breaking changes.

Installation
------------

:code:`pip install kusto-tool`

The main feature of `kusto-tool` is a Python expression API for generating
Kusto queries directly from Python code, using method chaining to mimic
Kusto Query Language (KQL)'s pipe-based query structure.

Quickstart (text-only)
----------------------

.. code-block:: python

    from kusto_tool import col, q
    from kusto_tool.function import sum_

    query = (
        q("StormEvents")
        .project("State", "EventType", "DamageProperty")
        .summarize(sum_damage=sum_("DamageProperty"), by=["State", "EventType"])
        .sort("sum_damage")
        .limit(20)
    )
    print(query.to_kql())

.. code-block:: text

    StormEvents
    | project
        State,
        EventType,
        DamageProperty
    | summarize
        sum_damage=sum(DamageProperty)
        by State, EventType
    | order by
        sum_damage
    | limit 20

Filters and expressions
-----------------------

Use ``col("Name")`` to create column references without schema, then build
expressions using Python operators.

.. code-block:: python

    from kusto_tool import col, q

    query = (
        q("StormEvents")
        .where(col("State") == "WA", col("DamageProperty") > 100000)
        .project("State", "EventType", "DamageProperty")
        .limit(10)
    )
    print(query)

.. code-block:: text

    StormEvents
    | where State == 'WA' and DamageProperty > 100000
    | project
        State,
        EventType,
        DamageProperty
    | limit 10

Aggregations and functions
--------------------------

Use functions from :mod:`kusto_tool.function` for common KQL aggregates.

.. code-block:: python

    from kusto_tool import q
    from kusto_tool.function import dcount, sum_

    query = (
        q("StormEvents")
        .summarize(
            sum_damage=sum_("DamageProperty"),
            distinct_states=dcount("State"),
            by=["EventType"],
        )
        .order("sum_damage")
    )

Schema-free by design
---------------------

Because this package is query-only, it never inspects live schema. You can
always pass column names as strings. Use ``col("Name")`` when you want to build
typed expressions without a schema.

Based on kusto-tool by Alex Kyllo. Vibecoded by Codex (ChatGPT).
