# kusto-tool

A high-level Python library to generate Azure Data Explorer (Kusto) query text
using a fluent expression API.

Based on kusto-tool by Alex Kyllo. Vibecoded by Codex (ChatGPT).

## Install

```bash
pip install kusto-tool
```

## Quickstart

```python
from kusto_tool import col, q
from kusto_tool.function import sum_

# No cluster/database context; just text generation
tbl = q("StormEvents")
query = (
    tbl.project("State", "EventType", "DamageProperty")
    .summarize(sum_damage=sum_("DamageProperty"), by=["State", "EventType"])
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
print(q("StormEvents").count().to_kql())
```

Expected output:
```text
StormEvents
| count
```

```python
# Filter with expression objects (no schema required)
query = (
    q("StormEvents")
    .where(col("State") == "WA", col("DamageProperty") > 100000)
    .project("State", "EventType", "DamageProperty")
    .limit(10)
)
print(query.to_kql())
```

Expected output:
```text
StormEvents
| where State == 'WA' and DamageProperty > 100000
| project
	State,
	EventType,
	DamageProperty
| limit 10
```

## API snapshot

- `q("Table")`: start a query from a table name.
- `col("Column")`: create a column reference for expressions.
- `TableExpr` methods: `project`, `where`, `summarize`, `join`, `extend`,
  `order`, `sort`, `limit`, `take`, `evaluate`, `distinct`, `sample`.
- `kusto_tool.function`: common Kusto functions like `sum`, `avg`, `dcount`.
- `str(query)` / `query.to_kql()`: render KQL text.

Experimental, work-in-progress, unstable API.
