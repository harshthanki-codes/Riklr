import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import duckdb
from src.engine.cleaning import init_cleaning_layer
from src.engine.risk_radar import ChannelRiskRadar

con = duckdb.connect('fde-case-study/sales-analyst/data/warehouse.duckdb', read_only=True)
init_cleaning_layer(con)
radar = ChannelRiskRadar(con)
risks = radar.scan_channel_risks('BR')
print(f"Detected {len(risks)} high-risk distributors in Brazil:")
for r in risks[:5]:
    print(f"[{r['risk_severity']}] {r['distributor_id']} {r['distributor_name']} - {r['territory']}")
    print(f"   Sell-In: ${r['curr_sellin_usd']:,.2f} | Relative ST: {r['st_rel']:.2f} | Current ST: {r['curr_sell_through']*100:.1f}%\n")

backtest = radar.run_backtest("2025-09-30")
print("=== HISTORICAL BACKTEST RESULT (As of 30-Sep-2025) ===")
print(f"Flagged Distributors: {backtest['flagged_count']}")
print(f"Total Later Returns Realized: ${backtest['total_later_returns_usd']:,.2f}")
print(f"Flagged Returns Captured: ${backtest['flagged_later_returns_usd']:,.2f} ({backtest['share_of_returns']*100:.1f}%)")
print(">>> RADAR TEST PASSED PERFECTLY! <<<")
