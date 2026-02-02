Overview of `kusto-tool`
========================

`kusto-tool` is a Python package providing a high-level interface for generating
Kusto query text.

This package is an experimental work-in-progress and the API is unstable.

Installation
------------

:code:`pip install kusto-tool`

The main feature of `kusto-tool` is a Python expression API for generating
Kusto queries directly from Python code, using method chaining to mimic
Kusto Query Language (KQL)'s pipe-based query structure.

.. code-block:: python

    from kusto_tool import cluster

    tbl = cluster("help").database("Samples").table("StormEvents")
    
    query = (
        tbl.project(tbl.State, tbl.EventType, tbl.DamageProperty)
        .summarize(sum_damage=tbl.DamageProperty.sum(), by=[tbl.State, tbl.EventType])
        .sort(tbl.sum_damage)
        .limit(20)
    )
    print(query)

    # cluster('help').database('Samples').['StormEvents']
    # | project
    #     State,
    #     EventType,
    #     DamageProperty
    # | summarize
    #     sum_damage=sum(DamageProperty)
    #     by State, EventType
    # | order by
    #     sum_damage
    # | limit 20

This package is query-only and does not connect to Azure Data Explorer.

Based on kusto-tool by Alex Kyllo. Vibecoded by Codex (ChatGPT).
