"""
Streamlit Web App: Governed AI Sales Analyst & Field Companion
Includes:
1. Executive 'Ask' Page: Natural Language & Simulated Voice Querying with Definition Bridge
2. Field Distributor 360 Pre-Visit Brief: 1-Page Offline HTML Export & Manager Notes
3. Channel-Risk Radar Sentinel: Real historical backtest with As-Of date selector
4. Data Health & Cleaning Receipts Audit Drawer
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import duckdb
from src.engine.governed_engine import GovernedEngine
from src.engine.risk_radar import ChannelRiskRadar
from src.engine.cleaning import get_cleaning_receipts
from src.nl.router import NLRouter
from src.nl.plan import IntentEnum, MetricEnum

st.set_page_config(
    page_title="Riklr Governed Sales Analyst",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Engine initialization
@st.cache_resource
def get_engine():
    return GovernedEngine()

engine = get_engine()
radar = ChannelRiskRadar(engine.con)
nl_router = NLRouter()

# Sidebar: User Authentication & Role Context
st.sidebar.title("🔐 User Persona & Security Scope")

users_df = engine.con.execute("""
    SELECT user_id, role, country, region, sub_region, territory_code 
    FROM users_and_roles 
    ORDER BY role, user_id
""").df()

selected_user_id = st.sidebar.selectbox(
    "Acting As User:",
    options=users_df['user_id'].tolist(),
    format_func=lambda uid: f"{uid} - {users_df[users_df['user_id']==uid]['role'].values[0]} ({users_df[users_df['user_id']==uid]['territory_code'].values[0] or users_df[users_df['user_id']==uid]['region'].values[0] or 'Global'})"
)

curr_user = engine.security.get_user(selected_user_id)
st.sidebar.info(
    f"**Role:** {curr_user['role']}\n\n"
    f"**Region:** {curr_user['region'] or 'Global'}\n\n"
    f"**Territory Scope:** {curr_user['territory_code'] or curr_user['sub_region'] or 'All'}"
)

# Pipeline Health Alert in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📡 Data Health Sentinel")
br_health = engine.freshness.check_region_freshness("BR")
if br_health["freshness_status"] != "HEALTHY":
    st.sidebar.warning(
        f"**Brazil Sync Lag**: {br_health['lag_days']} days behind.\n\n"
        f"Latest Date: {br_health['data_through']}\n\n"
        f"{br_health['warning']}"
    )
else:
    st.sidebar.success("All regional pipelines synced.")

# Cleaning Receipts Expander
receipts = get_cleaning_receipts(engine.con)
with st.sidebar.expander("🧹 Cleaning Receipts"):
    st.write(f"• Remapped territory codes: **{receipts['remapped_territory_codes']:,}**")
    st.write(f"• Deduplicated sell-in lines: **{receipts['duplicate_sell_in_lines']:,}**")
    st.write(f"• Deduplicated return rows: **{receipts['duplicate_returns']:,}**")
    st.write(f"• Negative invoice lines: **{receipts['negative_invoice_lines']:,}**")

# Main Navigation
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Ask Governed Analyst", 
    "🌉 Two Numbers Bridge",
    "📋 Distributor 360 Brief", 
    "⚠️ Channel-Risk Radar Sentinel"
])

# -------------------------------------------------------------
# TAB 1: ASK GOVERNED ANALYST
# -------------------------------------------------------------
with tab1:
    st.header("💬 Governed Sales Analyst")
    st.caption("Ask questions in English, Portuguese, or Romanized/Native Marathi & Hindi. Zero SQL hallucination with deterministic metric execution.")

    # Simulated voice / quick prompt selector
    sample_queries = [
        "Type my own question...",
        "Tiranex Agro Agencies chi baki kiti aahe? (Marathi voice note)",
        "mere distributor ka pending credit note kab aayega? (Hindi voice note)",
        "Quais revendas estao com risco de estoque alto? (Portuguese)",
        "What were our net sales in FY2026?",
        "What were gross sales for Vidarbha in FY2026?",
        "Show me total sales across all regions"
    ]
    picked_sample = st.selectbox("Simulated Voice Note / Quick Example:", sample_queries)

    if picked_sample == "Type my own question...":
        user_input = st.text_input("Enter Question:", placeholder="e.g. What were net sales in FY2026?")
    else:
        user_input = st.text_input("Enter Question:", value=picked_sample.split(" (")[0])

    if st.button("🚀 Submit Question", use_container_width=True):
        plan = nl_router.route_query(user_input, user_scope_territory=curr_user.get("territory_code"))

        if plan.intent == IntentEnum.OUT_OF_SCOPE:
            st.warning(f"🛑 {plan.refusal_reason}")
        elif plan.metric == MetricEnum.AMBIGUOUS_SALES:
            st.info("💡 **Ambiguity Resolved:** You asked for 'Sales'. Sales Ops and Finance define Sales differently. Displaying both figures with the bridge:")
            
            c1, c2 = st.columns(2)
            res_gross = engine.execute_sales_query(selected_user_id, metric_choice="GROSS_SALES", fiscal_year=2026)
            res_net = engine.execute_sales_query(selected_user_id, metric_choice="NET_SALES", fiscal_year=2026)
            
            tot_g = sum(r['gross_sales_usd'] for r in res_gross['data'])
            tot_n = sum(r['net_sales_usd'] for r in res_net['data'])
            
            c1.metric("Gross Sales (Sales Ops M01)", f"${tot_g/1e6:,.2f}M USD", help="Gross invoiced before returns/credits")
            c2.metric("Net Sales (Finance M02)", f"${tot_n/1e6:,.2f}M USD", delta=f"-${(tot_g-tot_n)/1e6:,.2f}M deductions", delta_color="inverse")
            
            st.markdown("👉 *See the 'Two Numbers Bridge' tab for the full waterfall reconciliation.*")
        else:
            metric_arg = "GROSS_SALES" if plan.metric == MetricEnum.M01_GROSS_SALES else "NET_SALES"
            res = engine.execute_sales_query(selected_user_id, metric_choice=metric_arg, territory=plan.territory, fiscal_year=plan.fiscal_year)
            
            if not res["success"]:
                st.error(f"🛑 {res['message']}")
            else:
                tf = res["trust_footer"]
                df_res = pd.DataFrame(res["data"])
                
                # Answer summary
                tot_val = sum(r['net_sales_usd'] if metric_arg == "NET_SALES" else r['gross_sales_usd'] for r in res['data'])
                st.subheader(f"📊 Result: **${tot_val/1e6:,.2f}M USD**")
                
                # Trust Chips
                ch1, ch2, ch3 = st.columns(3)
                ch1.info(f"**Definition:** {tf['metric_name']} ({tf['owner']})")
                ch2.info(f"**Data Through:** {tf['data_through']}")
                ch3.info(f"**Scope:** {tf['user_scope']}")
                
                if tf["freshness_warning"]:
                    st.warning(f"⚠️ {tf['freshness_warning']}")
                if tf["field_caveat"]:
                    st.caption(f"ℹ️ {tf['field_caveat']}")

                with st.expander("🔍 Why this number? (Query Plan & Bound SQL)"):
                    st.json(plan.dict())
                    st.code(tf["executed_sql"], language="sql")

                st.dataframe(df_res, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: TWO NUMBERS BRIDGE
# -------------------------------------------------------------
with tab2:
    st.header("🌉 Two Numbers, One Bridge (Waterfall Reconciliation)")
    st.caption("Settles the dispute between Sales Ops and Finance on screen: reconciling Gross Sell-In to Clean Net Sales.")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        bridge_fy = st.selectbox("Fiscal Year for Bridge:", [2026, 2025])
    with col_b2:
        bridge_reg = st.selectbox("Region Filter for Bridge:", ["GLOBAL", "BR", "IN", "NA", "EU"])
        reg_val = None if bridge_reg == "GLOBAL" else bridge_reg

    if st.button("Generate Waterfall Bridge", use_container_width=True):
        res = engine.execute_sales_query(selected_user_id, metric_choice="NET_SALES", region=reg_val, fiscal_year=bridge_fy)
        if res["success"]:
            tot_gross = sum(r["gross_sales_usd"] for r in res["data"])
            tot_neg = sum(r.get("negative_lines_usd", 0) for r in res["data"])
            tot_ret = sum(r["returns_usd"] for r in res["data"])
            tot_cred = sum(r["scheme_credits_usd"] for r in res["data"])
            tot_net = sum(r["net_sales_usd"] for r in res["data"])

            bridge_df = pd.DataFrame([
                {"Component": "1. Gross Sales (Sales Ops M01)", "Amount (USD)": f"${tot_gross:,.2f}"},
                {"Component": "2. Less: Negative Invoice Lines", "Amount (USD)": f"-${tot_neg:,.2f}"},
                {"Component": "3. Less: Credited Returns", "Amount (USD)": f"-${tot_ret:,.2f}"},
                {"Component": "4. Less: Scheme & Rebate Credits", "Amount (USD)": f"-${tot_cred:,.2f}"},
                {"Component": "5. Clean Net Sales (Finance M02)", "Amount (USD)": f"${tot_net:,.2f}"}
            ])
            st.table(bridge_df)
            st.success(f"Deductions total **${(tot_gross - tot_net)/1e6:.2f}M USD** across returns and scheme credits.")

# -------------------------------------------------------------
# TAB 3: DISTRIBUTOR 360 PRE-VISIT BRIEF
# -------------------------------------------------------------
with tab3:
    st.header("📋 Field Distributor 360 Pre-Visit Brief")
    st.caption("Replaces the paper notebook with governed numbers before entering a distributor meeting.")

    allowed_terr = engine.security.get_allowed_territories(selected_user_id, "sell_in")
    if allowed_terr is None:
        dist_options = engine.con.execute("SELECT distributor_id, distributor_name, territory_code FROM distributors ORDER BY distributor_id").df()
    else:
        t_list = ", ".join(f"'{t}'" for t in allowed_terr)
        dist_options = engine.con.execute(f"SELECT distributor_id, distributor_name, territory_code FROM distributors WHERE territory_code IN ({t_list}) ORDER BY distributor_id").df()

    if dist_options.empty:
        st.warning("No distributors accessible under your current role permissions.")
    else:
        dist_id = st.selectbox(
            "Select Distributor:",
            options=dist_options["distributor_id"].tolist(),
            format_func=lambda d: f"{d} - {dist_options[dist_options['distributor_id']==d]['distributor_name'].values[0]} ({dist_options[dist_options['distributor_id']==d]['territory_code'].values[0]})"
        )
        
        brief_lang = st.radio("Display Language:", ["English", "मराठी (Marathi)", "Português", "हिंदी (Hindi)"], horizontal=True)

        if st.button("📄 Generate 1-Page Pre-Visit Brief", use_container_width=True):
            brief = engine.get_distributor_previsit_brief(user_id=selected_user_id, distributor_id=dist_id)
            if not brief["success"]:
                st.error(brief["message"])
            else:
                d = brief["distributor"]
                c = brief["commercial"]
                r = brief["receivables"]
                stuck = brief["pending_credits"]
                redacted = brief["redacted_sections"]

                st.subheader(f"🏢 {d['name']} ({d['id']}) — Territory: {d['territory']}")
                
                if redacted:
                    for sec in redacted:
                        st.info(f"🔒 {sec}")

                k1, k2, k3 = st.columns(3)
                if c["sell_in_amount"] is not None:
                    k1.metric("FY26 Sell-In", f"{c['sell_in_amount']:,.0f} {d['currency']}")
                else:
                    k1.metric("FY26 Packs Sold", f"{c['packs_sold']:,} packs")
                
                k2.metric("Scan Sell-Through", f"{c['curr_sell_through_pct']}%", delta=f"vs {c['prev_sell_through_pct']}% last season")
                k3.metric("Self-Relative Sell-Through", f"{c['self_relative_sell_through']}x", delta=c['channel_health'])

                c_left, c_right = st.columns(2)
                
                with c_left:
                    st.markdown("### 💳 Receivables Aging")
                    if r:
                        st.write(f"**Snapshot Date:** {r['snapshot_date']}")
                        aging_df = pd.DataFrame([{
                            "Total Outstanding": f"{r['total_outstanding']:,.0f}",
                            "Not Due": f"{r['not_due']:,.0f}",
                            "Overdue 90+ Days": f"{r['overdue_90_plus']:,.0f}",
                            "Disputed": f"{r['disputed']:,.0f}"
                        }])
                        st.table(aging_df)
                    else:
                        st.info("Receivables data redacted for your role.")

                with c_right:
                    st.markdown(f"### ⏳ Pending Scheme Credits ({len(stuck)})")
                    if stuck:
                        st.warning(f"Found {len(stuck)} pending credits!")
                        st.table(pd.DataFrame(stuck)[["credit_id", "scheme_name", "amount_local", "age_days", "typical_days_in_region"]])
                    else:
                        st.success("No pending scheme credits.")

# -------------------------------------------------------------
# TAB 4: CHANNEL-RISK RADAR
# -------------------------------------------------------------
with tab4:
    st.header("⚠️ Channel-Risk Radar Sentinel")
    st.caption("Early warning of inventory loading and return hazards using historical self-relative sell-through.")

    as_of = st.date_input("As-Of Date for Backtest:", value=pd.to_datetime("2025-09-30"))
    as_of_str = str(as_of)
    
    if st.button("🔍 Execute Risk Backtest", use_container_width=True):
        bt = radar.run_backtest(as_of_date=as_of_str, threshold=0.70)
        
        st.subheader(f"🚨 Backtest Results as of {as_of_str}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Distributors Flagged", bt["flagged_count"])
        c2.metric("Later Returns Captured", f"{bt['share_of_returns']*100:.1f}%", help="Share of subsequent return dollars correctly predicted")
        c3.metric("Hits in Top Returners", f"{bt['hits_in_top_returners']} / {bt['flagged_count']}")

        if bt["flagged_distributors"]:
            st.dataframe(pd.DataFrame(bt["flagged_distributors"])[["distributor_id", "distributor_name", "territory", "curr_sell_through", "prev_sell_through", "st_rel", "rainfall_pct_8w", "risk_severity"]], use_container_width=True)
            st.success(f"Captured **{bt['share_of_returns']*100:.1f}%** of later returns 4-5 months before return credit notes were raised!")
