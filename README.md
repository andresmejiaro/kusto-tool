# kusto-tool

A high-level Python library to generate Azure Data Explorer (Kusto) query text
using a fluent expression API.

Based on kusto-tool by Alex Kyllo. Vibecoded by Codex (ChatGPT).

## Demo

```python
from kusto_tool import table
from kusto_tool.function import sum

# No cluster/database context; just text generation
tbl = table("StormEvents")
query = (
    tbl.project("State", "EventType", "DamageProperty")
    .summarize(sum_damage=sum("DamageProperty"), by=["State", "EventType"])
    .sort("sum_damage")
    .limit(20)
)
print(query.to_kql())
```

Expected output:
```text
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
```

```python
# Simple count
print(table("StormEvents").count().to_kql())
```

Expected output:
```text
StormEvents
| count
```

Experimental, work-in-progress, unstable API.
