from src.engine.governed_engine import GovernedEngine

def test_governed_engine():
    engine = GovernedEngine()
    
    print("=== TEST 1: Global Finance Controller (U003) Net Sales (USD) ===")
    res1 = engine.execute_sales_query(user_id="U003", metric_choice="NET_SALES", fiscal_year=2026)
    print("Test 1 Net Sales Rows:", res1["row_count"])
    total_net = sum(r["net_sales_usd"] for r in res1["data"])
    print(f"Global Net Sales USD: ${total_net:,.2f}")
    assert res1["success"] is True
    assert total_net > 0

    print("\n=== TEST 2: Vidarbha Territory Manager Querying Own Territory ===")
    u_vid = engine.con.execute(
        "SELECT user_id, role, territory_code FROM users_and_roles WHERE territory_code = 'IN-W01' LIMIT 1"
    ).fetchone()
    print("Vidarbha user:", u_vid)
    vid_uid = u_vid[0]
    res2 = engine.execute_sales_query(user_id=vid_uid, metric_choice="GROSS_SALES", territory="IN-W01")
    print("Own Territory Result:", res2["success"], res2["data"])
    assert res2["success"] is True
    assert len(res2["data"]) > 0

    print("\n=== TEST 3: Vidarbha Manager Probing Out-Of-Territory Data (BR-S01) ===")
    res3 = engine.execute_sales_query(user_id=vid_uid, metric_choice="GROSS_SALES", territory="BR-S01")
    print("Cross Territory Result:", res3["success"], "| Error:", res3.get("message"))
    assert res3["success"] is False
    assert res3["error_type"] == "ACCESS_DENIED"

    print("\n=== TEST 4: Distributor Pre-Visit Brief (D011) ===")
    # Pick a distributor in IN-W01
    d_row = engine.con.execute("SELECT distributor_id FROM distributors WHERE territory_code = 'IN-W01' LIMIT 1").fetchone()
    if d_row:
        dist_id = d_row[0]
        brief = engine.get_distributor_previsit_brief(user_id=vid_uid, distributor_id=dist_id)
        print("Distributor Brief for:", dist_id)
        print("Profile:", brief["distributor"])
        print("Commercial:", brief["commercial"])
        print("Receivables:", brief["receivables"])
        print("Stuck Credits Count:", len(brief["stuck_credits"]))
        assert brief["success"] is True

    print("\n>>> ALL GOVERNED ENGINE TESTS PASSED PERFECTLY! <<<")

if __name__ == "__main__":
    test_governed_engine()
