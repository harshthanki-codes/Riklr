import duckdb
from src.engine.risk_radar import ChannelRiskRadar

con = duckdb.connect('fde-case-study/sales-analyst/data/warehouse.duckdb', read_only=True)
radar = ChannelRiskRadar(con)
risks = radar.scan_channel_risks('BR')
print(f"Detected {len(risks)} high-risk distributors in Brazil:")
for r in risks[:5]:
    print(f"[{r['risk_severity']}] {r['distributor_id']} {r['distributor_name']} - {r['territory']}")
    print(f"   Sell-In: ${r['sell_in_usd']:,.2f} | Returns: ${r['actual_returns_usd']:,.2f} | Sell-Through: {r['sell_through_rate']*100:.1f}%\n")
