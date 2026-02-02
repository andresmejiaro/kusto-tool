# kusto-tool

A high-level Python library to generate Azure Data Explorer (Kusto) query text
using a fluent expression API.

Based on kusto-tool by Alex Kyllo. Vibecoded by Codex (ChatGPT).

## Demo

```python
from kusto_tool import cluster, table, db

# With cluster/database context
tbl = cluster("help").database("Samples").table("StormEvents")
query = (
    tbl.project(tbl.State, tbl.EventType, tbl.DamageProperty)
    .summarize(sum_damage=tbl.DamageProperty.sum(), by=[tbl.State, tbl.EventType])
    .sort(tbl.sum_damage)
    .limit(20)
)
print(query.to_kql())
```

Expected output:
```text
cluster('help').database('Samples').['StormEvents']
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
```

```python
# Without context (just table name)
print(table("StormEvents").count().to_kql())
```

Expected output:
```text
StormEvents
| count
```

```python
# Database-only context
print(db("Samples").table("StormEvents").limit(5).to_kql())
```

Expected output:
```text
database('Samples').['StormEvents']
| limit 5
```

Experimental, work-in-progress, unstable API.
