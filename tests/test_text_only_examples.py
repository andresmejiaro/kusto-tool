from kusto_tool import col, query
from kusto_tool.function import sum_


def test_text_only_summarize_example():
    query = (
        query("StormEvents")
        .project("State", "EventType", "DamageProperty")
        .summarize(sum_damage=sum_("DamageProperty"), by=["State", "EventType"])
        .sort("sum_damage")
        .limit(20)
    )
    expected = """StormEvents
| project
\tState,
\tEventType,
\tDamageProperty
| summarize
\tsum_damage=sum(DamageProperty)
\tby State, EventType
| order by
\tsum_damage
| limit 20
"""
    assert str(query) == expected


def test_text_only_filter_example():
    query = (
        query("StormEvents")
        .where(col("State") == "WA", col("DamageProperty") > 100000)
        .project("State", "EventType", "DamageProperty")
        .limit(10)
    )
    expected = """StormEvents
| where State == 'WA' and DamageProperty > 100000
| project
\tState,
\tEventType,
\tDamageProperty
| limit 10
"""
    assert str(query) == expected
