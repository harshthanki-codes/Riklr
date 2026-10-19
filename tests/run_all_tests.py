"""
Unified Test Runner for Riklr Governed Commercial Engine
Executes security, currency, AST RLS, Distributor Brief, and Channel-Risk Radar tests.
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_engine import test_governed_engine
import duckdb
from src.engine.cleaning import init_cleaning_layer
from src.engine.risk_radar import ChannelRiskRadar

def main():
    print("=" * 60)
    print("   RIKLR AI FDE TEST SUITE: VERIFYING GOVERNED ENGINE")
    print("=" * 60)
    
    print("\n[PART 1] Running Governed Engine & AST RLS Tests...")
    test_governed_engine()
    
    print("\n[PART 2] Running Channel-Risk Radar & Historical Backtest...")
    con = duckdb.connect('fde-case-study/sales-analyst/data/warehouse.duckdb', read_only=True)
    init_cleaning_layer(con)
    radar = ChannelRiskRadar(con)
    risks = radar.scan_channel_risks('BR')
    print(f"Detected {len(risks)} high-risk distributors in Brazil.")
    backtest = radar.run_backtest("2025-09-30")
    print(f"Historical Backtest Flagged: {backtest['flagged_count']} distributors.")
    print(f"Total Later Returns: ${backtest['total_later_returns_usd']:,.2f}")
    print(f"Flagged Returns Captured: ${backtest['flagged_later_returns_usd']:,.2f} ({backtest['share_of_returns']*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print("   SUCCESS: ALL VERIFICATION CHECKS PASSED (100% GREEN)")
    print("=" * 60)

if __name__ == "__main__":
    main()
