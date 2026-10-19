"""
Production-Grade Enterprise Streamlit UI: Riklr Governed Commercial Sales Platform
Aesthetic: Palantir Foundry / Snowflake Horizon / Bloomberg Terminal Tier.
Tabs:
1. 💬 Governed Sales Analyst (NL Querying + Trust Footer + Bound AST Inspect)
2. 🌉 Two Numbers Bridge (Executive Gross-to-Net Waterfall)
3. 📋 Field Distributor 360 Brief (Role-Redacted, Multilingual, Inactive Dealer Radar)
4. ⚠️ Channel-Risk Radar Sentinel (Honest As-Of Backtest against $8.0M Brazil Returns)
5. 🛡️ Working Capital & Credit Guard (Overdraft Breaches, 350% Utilization, Disputed Receivables)
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
from src.engine.credit_guard import CreditExposureGuard
from src.engine.cleaning import get_cleaning_receipts
from src.nl.router import NLRouter
from src.nl.plan import IntentEnum, MetricEnum
from src.ui.theme import CUSTOM_CSS

st.set_page_config(
    page_title="Riklr Commercial Intelligence Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Enterprise CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Engine initialization
@st.cache_resource
def get_engine():
    return GovernedEngine()

engine = get_engine()
radar = ChannelRiskRadar(engine.con)
credit_guard = CreditExposureGuard(engine.con)
nl_router = NLRouter()

# -------------------------------------------------------------
# SIDEBAR: ENTERPRISE PERSONA & PERMISSION CONTEXT
# -------------------------------------------------------------
st.sidebar.markdown("""
<div style="padding: 10px 0 16px 0;">
    <span style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">Riklr Commercial Engine</span>
    <span class="pill-badge badge-primary">v2.4 Governed</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.caption("PHYSICAL ROW-LEVEL SECURITY CONTEXT")

users_df = engine.con.execute("""
    SELECT user_id, role, country, region, sub_region, territory_code 
    FROM users_and_roles 
    ORDER BY role, user_id
""").df()

selected_user_id = st.sidebar.selectbox(
    "Active User Persona:",
    options=users_df['user_id'].tolist(),
    format_func=lambda uid: f"{uid} - {users_df[users_df['user_id']==uid]['role'].values[0]} ({users_df[users_df['user_id']==uid]['territory_code'].values[0] or users_df[users_df['user_id']==uid]['region'].values[0] or 'Global'})"
)

curr_user = engine.security.get_user(selected_user_id)
st.sidebar.markdown(f"""
<div style="background: #161D2B; border: 1px solid #232D42; border-radius: 6px; padding: 12px; margin-top: 6px; margin-bottom: 16px;">
    <div style="font-size: 0.75rem; color: #8B949E; text-transform: uppercase;">Authenticated Role</div>
    <div style="font-weight: 600; color: #58A6FF;">{curr_user['role']}</div>
    <div style="font-size: 0.75rem; color: #8B949E; text-transform: uppercase; margin-top: 8px;">Enforced Scope</div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #E6EDF3;">{curr_user['territory_code'] or curr_user['sub_region'] or 'GLOBAL UNRESTRICTED'}</div>
</div>
""", unsafe_allow_html=True)

# Data Freshness Sentinel
br_health = engine.freshness.check_region_freshness("BR")
st.sidebar.markdown("### 📡 Data Health Sentinel")
if br_health["freshness_status"] != "HEALTHY":
    st.sidebar.markdown(f"""
    <div style="background: rgba(210, 153, 34, 0.1); border: 1px solid rgba(210, 153, 34, 0.3); border-radius: 6px; padding: 10px; font-size: 0.8rem; color: #D29922;">
        <strong>⚠️ Brazil Pipeline Lag ({br_health['lag_days']}d behind)</strong><br>
        Current to: {br_health['data_through']}<br>
        15/52 loads succeeded post ERP sync.
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.success("All regional pipelines synced.")

# Cleaning Receipts
receipts = get_cleaning_receipts(engine.con)
with st.sidebar.expander("🧹 Warehouse Cleaning Receipts"):
    st.markdown(f"""
    - **{receipts['remapped_territory_codes']:,}** Legacy / Malformed Codes Remapped
    - **{receipts['duplicate_sell_in_lines']:,}** Duplicate Invoices Deduplicated
    - **{receipts['duplicate_returns']:,}** Duplicate Return Rows Removed
    - **{receipts['negative_invoice_lines']:,}** Negative Lines Handled as Returns
    """)

# -------------------------------------------------------------
# MAIN APP HEADER & WORKFLOW TABS
# -------------------------------------------------------------
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1E2638; padding-bottom: 12px; margin-bottom: 20px;">
    <div>
        <h2 style="margin: 0; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">Commercial Sales Intelligence Platform</h2>
        <p style="margin: 2px 0 0 0; color: #8B949E; font-size: 0.85rem;">Governed Semantic Data Engine • Palantir & Databricks Architecture Standard</p>
    </div>
    <div>
        <span class="pill-badge badge-success">● DuckDB In-Memory</span>
        <span class="pill-badge badge-primary">Deterministic SQL</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Governed Analyst",
    "🌉 Two Numbers Bridge",
    "📋 Field Distributor 360",
    "⚠️ Channel-Risk Radar",
    "🛡️ Working Capital & Credit Guard"
])

# -------------------------------------------------------------
# TAB 1: GOVERNED ANALYST
# -------------------------------------------------------------
with tab1:
    st.markdown("### 💬 Governed Query Engine (Natural Language & Voice)")
    st.caption("Ask questions across regions in English, Portuguese, or Romanized Hindi/Marathi. Grounded in deterministic metrics with no SQL hallucination.")

    c_q1, c_q2 = st.columns([3, 1])
    with c_q1:
        quick_prompts = [
            "Custom query...",
            "What were net sales in FY2026 across regions?",
            "Show me gross sales for Vidarbha in FY2026",
            "Tiranex Agro Agencies chi baki kiti aahe? (Marathi)",
            "mere distributor ka pending credit note kab aayega? (Hindi)",
            "Quais revendas estao com risco de estoque alto? (Portuguese)",
            "Total sales (Ambiguity Test)"
        ]
        picked_sample = st.selectbox("Quick Voice Note / Scenario Preset:", quick_prompts)
        if picked_sample == "Custom query...":
            nl_input = st.text_input("Enter natural language question:", placeholder="e.g. What were our net sales in FY2026?")
        else:
            nl_input = st.text_input("Enter natural language question:", value=picked_sample.split(" (")[0])

    with c_q2:
        st.write("")
        st.write("")
        run_btn = st.button("🚀 Execute Query", use_container_width=True)

    if run_btn and nl_input:
        plan = nl_router.route_query(nl_input, user_scope_territory=curr_user.get("territory_code"))

        if plan.intent == IntentEnum.OUT_OF_SCOPE:
            st.error(f"🛑 **Refusal**: {plan.refusal_reason}")
        elif plan.metric == MetricEnum.AMBIGUOUS_SALES:
            st.warning("⚖️ **Ambiguity Detected**: 'Sales' has two conflicting corporate definitions. Showing both with reconciliation:")
            
            res_g = engine.execute_sales_query(selected_user_id, metric_choice="GROSS_SALES", fiscal_year=2026)
            res_n = engine.execute_sales_query(selected_user_id, metric_choice="NET_SALES", fiscal_year=2026)
            
            tot_g = sum(r['gross_sales_usd'] for r in res_g['data'])
            tot_n = sum(r['net_sales_usd'] for r in res_n['data'])
            gap = tot_g - tot_n
            
            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Gross Sales (Sales Ops M01)</div>
                    <div class="metric-value">${tot_g/1e6:,.2f}M</div>
                    <div class="metric-delta neutral">Order Date • No Deductions</div>
                </div>
                """, unsafe_allow_html=True)
            with k2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Net Sales (Finance M02)</div>
                    <div class="metric-value">${tot_n/1e6:,.2f}M</div>
                    <div class="metric-delta positive">Invoice Date • FX Adjusted</div>
                </div>
                """, unsafe_allow_html=True)
            with k3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Deduction Variance</div>
                    <div class="metric-value">-${gap/1e6:,.2f}M</div>
                    <div class="metric-delta negative">Returns + Schemes + Negatives</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            metric_choice = "GROSS_SALES" if plan.metric == MetricEnum.M01_GROSS_SALES else "NET_SALES"
            res = engine.execute_sales_query(
                user_id=selected_user_id,
                metric_choice=metric_choice,
                territory=plan.territory,
                fiscal_year=plan.fiscal_year
            )

            if not res["success"]:
                st.error(f"🛑 {res['message']}")
            else:
                tf = res["trust_footer"]
                df_res = pd.DataFrame(res["data"])
                tot_val = sum(r['net_sales_usd'] if metric_choice == "NET_SALES" else r['gross_sales_usd'] for r in res['data'])

                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 20px;">
                    <div class="metric-title">{tf['metric_name']} (Total)</div>
                    <div class="metric-value">${tot_val/1e6:,.2f}M USD</div>
                    <div class="metric-delta neutral">Filtered to authorized scope: <code>{tf['user_scope']}</code></div>
                </div>
                """, unsafe_allow_html=True)

                # Trust Footer Details
                st.markdown(f"""
                <div class="trust-footer">
                    <div style="display: flex; gap: 20px; font-size: 0.85rem; color: #8B949E; margin-bottom: 8px;">
                        <span><strong>Metric ID:</strong> <code style="color: #58A6FF;">{tf['metric_id']}</code></span>
                        <span><strong>Owner:</strong> {tf['owner']}</span>
                        <span><strong>Data Freshness:</strong> {tf['data_through']}</span>
                    </div>
                    {f'<div style="color: #D29922; font-size: 0.8rem; margin-top: 4px;">⚠️ {tf["freshness_warning"]}</div>' if tf["freshness_warning"] else ''}
                </div>
                """, unsafe_allow_html=True)

                with st.expander("🔍 Certified Query Plan & Bound AST SQL"):
                    st.json(plan.dict())
                    st.code(tf["executed_sql"], language="sql")

                st.dataframe(df_res, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: TWO NUMBERS BRIDGE
# -------------------------------------------------------------
with tab2:
    st.markdown("### 🌉 Two Numbers, One Bridge (Executive Waterfall)")
    st.caption("Reconciles Sales Operations Gross Volume to Finance Audited Net Sales across currencies.")

    b_c1, b_c2 = st.columns(2)
    with b_c1:
        fy_b = st.selectbox("Fiscal Year:", [2026, 2025])
    with b_c2:
        reg_b = st.selectbox("Region Filter:", ["GLOBAL", "BR", "IN", "NA", "EU"])
        reg_val = None if reg_b == "GLOBAL" else reg_b

    res_bridge = engine.execute_sales_query(selected_user_id, metric_choice="NET_SALES", region=reg_val, fiscal_year=fy_b)
    if res_bridge["success"]:
        tot_gross = sum(r["gross_sales_usd"] for r in res_bridge["data"])
        tot_neg = sum(r.get("negative_lines_usd", 0) for r in res_bridge["data"])
        tot_ret = sum(r["returns_usd"] for r in res_bridge["data"])
        tot_cred = sum(r["scheme_credits_usd"] for r in res_bridge["data"])
        tot_net = sum(r["net_sales_usd"] for r in res_bridge["data"])

        w1, w2, w3, w4 = st.columns(4)
        w1.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Gross Invoiced</div>
            <div class="metric-value">${tot_gross/1e6:,.2f}M</div>
            <div class="metric-delta neutral">100% Volume Baseline</div>
        </div>
        """, unsafe_allow_html=True)
        w2.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Product Returns</div>
            <div class="metric-value">-${tot_ret/1e6:,.2f}M</div>
            <div class="metric-delta negative">{(tot_ret/tot_gross)*100:.1f}% of Gross</div>
        </div>
        """, unsafe_allow_html=True)
        w3.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Scheme Rebates</div>
            <div class="metric-value">-${tot_cred/1e6:,.2f}M</div>
            <div class="metric-delta negative">{(tot_cred/tot_gross)*100:.1f}% of Gross</div>
        </div>
        """, unsafe_allow_html=True)
        w4.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Audited Net Sales</div>
            <div class="metric-value">${tot_net/1e6:,.2f}M</div>
            <div class="metric-delta positive">Finance Recognized (M02)</div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        bridge_table = pd.DataFrame([
            {"Stage": "1. Gross Sales (Sales Ops M01)", "Amount (USD)": f"${tot_gross:,.2f}", "Status": "Invoiced"},
            {"Stage": "2. Less: Negative Invoice Lines", "Amount (USD)": f"-${tot_neg:,.2f}", "Status": "Deduction"},
            {"Stage": "3. Less: Credited Returns", "Amount (USD)": f"-${tot_ret:,.2f}", "Status": "Deduction"},
            {"Stage": "4. Less: Scheme & Loyalty Credits", "Amount (USD)": f"-${tot_cred:,.2f}", "Status": "Deduction"},
            {"Stage": "5. Clean Net Sales (Finance M02)", "Amount (USD)": f"${tot_net:,.2f}", "Status": "Audited Net"}
        ])
        st.table(bridge_table)

# -------------------------------------------------------------
# TAB 3: FIELD DISTRIBUTOR 360 BRIEF
# -------------------------------------------------------------
with tab3:
    st.markdown("### 📋 Field Distributor 360 Pre-Visit Brief")
    st.caption("Replaces the paper notebook with real-time governed numbers before entering a dealer or distributor meeting.")

    allowed_terr = engine.security.get_allowed_territories(selected_user_id, "sell_in")
    if allowed_terr is None:
        dist_options = engine.con.execute("SELECT distributor_id, distributor_name, territory_code FROM distributors ORDER BY distributor_id").df()
    else:
        t_list = ", ".join(f"'{t}'" for t in allowed_terr)
        dist_options = engine.con.execute(f"SELECT distributor_id, distributor_name, territory_code FROM distributors WHERE territory_code IN ({t_list}) ORDER BY distributor_id").df()

    if dist_options.empty:
        st.warning("No distributors accessible under your current role permissions.")
    else:
        d_col1, d_col2 = st.columns([2, 1])
        with d_col1:
            dist_id = st.selectbox(
                "Select Distributor Account:",
                options=dist_options["distributor_id"].tolist(),
                format_func=lambda d: f"{d} - {dist_options[dist_options['distributor_id']==d]['distributor_name'].values[0]} ({dist_options[dist_options['distributor_id']==d]['territory_code'].values[0]})"
            )
        with d_col2:
            brief_lang = st.radio("Language:", ["English", "मराठी (Marathi)", "Português", "हिंदी (Hindi)"], horizontal=True)

        brief = engine.get_distributor_previsit_brief(user_id=selected_user_id, distributor_id=dist_id)
        if not brief["success"]:
            st.error(brief["message"])
        else:
            d = brief["distributor"]
            c = brief["commercial"]
            r = brief["receivables"]
            stuck = brief["pending_credits"]
            redacted = brief["redacted_sections"]

            if redacted:
                for sec in redacted:
                    st.info(f"🔒 {sec}")

            # Top KPI metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">FY26 Sell-In</div>
                <div class="metric-value">{f"{c['sell_in_amount']:,.0f} {d['currency']}" if c['sell_in_amount'] else f"{c['packs_sold']:,} packs"}</div>
                <div class="metric-delta neutral">{c['packs_sold']:,} Total Packs</div>
            </div>
            """, unsafe_allow_html=True)

            m2.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Scan Sell-Through</div>
                <div class="metric-value">{c['curr_sell_through_pct']}%</div>
                <div class="metric-delta {'positive' if c['self_relative_sell_through']>=0.7 else 'negative'}">vs {c['prev_sell_through_pct']}% prior season</div>
            </div>
            """, unsafe_allow_html=True)

            m3.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Relative Ratio</div>
                <div class="metric-value">{c['self_relative_sell_through']}x</div>
                <div class="metric-delta {'positive' if c['self_relative_sell_through']>=0.7 else 'negative'}">{c['channel_health']}</div>
            </div>
            """, unsafe_allow_html=True)

            m4.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Pending Rebates</div>
                <div class="metric-value">{len(stuck)}</div>
                <div class="metric-delta {'negative' if len(stuck)>0 else 'positive'}">{f"{sum(s['amount_local'] for s in stuck):,.0f} {d['currency']}" if stuck else "Zero Stuck"}</div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("#### 💳 Receivables Aging Breakdown")
                if r:
                    rec_df = pd.DataFrame([{
                        "Total Outstanding": f"{r['total_outstanding']:,.0f}",
                        "Not Due": f"{r['not_due']:,.0f}",
                        "Overdue 90+ Days": f"{r['overdue_90_plus']:,.0f}",
                        "Disputed": f"{r['disputed']:,.0f}"
                    }])
                    st.table(rec_df)
                else:
                    st.info("Receivables data redacted for your role.")

            with col_r:
                st.markdown(f"#### ⏳ Pending Scheme Credits ({len(stuck)})")
                if stuck:
                    st.dataframe(pd.DataFrame(stuck)[["credit_id", "scheme_name", "amount_local", "age_days", "typical_days_in_region"]], use_container_width=True)
                else:
                    st.success("No accrued scheme credits pending issue.")

# -------------------------------------------------------------
# TAB 4: CHANNEL-RISK RADAR
# -------------------------------------------------------------
with tab4:
    st.markdown("### ⚠️ Channel-Risk Radar Sentinel (Honest Historical Backtest)")
    st.caption("Detects dangerous inventory loading where sell-in volume diverges from end-grower scan sell-through before costly returns occur.")

    as_of = st.date_input("Backtest As-Of Evaluation Date:", value=pd.to_datetime("2025-09-30"))
    bt = radar.run_backtest(as_of_date=str(as_of), threshold=0.70)

    rb1, rb2, rb3 = st.columns(3)
    rb1.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Distributors Flagged</div>
        <div class="metric-value">{bt['flagged_count']} / 32</div>
        <div class="metric-delta neutral">Threshold: &lt; 0.70 Relative ST</div>
    </div>
    """, unsafe_allow_html=True)

    rb2.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Subsequent Returns Captured</div>
        <div class="metric-value">{bt['share_of_returns']*100:.1f}%</div>
        <div class="metric-delta positive">90-Day Early Warning Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

    rb3.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Hits in Top Returners</div>
        <div class="metric-value">{bt['hits_in_top_returners']} / {bt['flagged_count']}</div>
        <div class="metric-delta positive">High Precision Hazard Scoring</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if bt["flagged_distributors"]:
        st.dataframe(
            pd.DataFrame(bt["flagged_distributors"])[["distributor_id", "distributor_name", "territory", "curr_sell_through", "prev_sell_through", "st_rel", "rainfall_pct_8w", "risk_severity"]],
            use_container_width=True
        )

# -------------------------------------------------------------
# TAB 5: WORKING CAPITAL & CREDIT GUARD
# -------------------------------------------------------------
with tab5:
    st.markdown("### 🛡️ Working Capital & Credit Exposure Guard")
    st.caption("Identifies extreme credit limit breaches (>100% utilization) and isolates 90+ day disputed receivables.")

    breaches = credit_guard.get_overdraft_breaches(snapshot_date="2026-08-31")
    
    cb1, cb2, cb3 = st.columns(3)
    cb1.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Accounts in Overdraft</div>
        <div class="metric-value">{len(breaches)}</div>
        <div class="metric-delta negative">Exceeding Sanctioned Limit</div>
    </div>
    """, unsafe_allow_html=True)

    top_util = breaches[0]["utilization_pct"] if breaches else 0
    cb2.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Peak Credit Utilization</div>
        <div class="metric-value">{top_util:.1f}%</div>
        <div class="metric-delta negative">{breaches[0]['distributor_name'] if breaches else ''}</div>
    </div>
    """, unsafe_allow_html=True)

    disputed_total = sum(b['disputed'] for b in breaches if b['currency'] == 'INR')
    cb3.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">India Disputed Receivables</div>
        <div class="metric-value">₹{disputed_total/1e6:.1f}M</div>
        <div class="metric-delta negative">Tied directly to stuck credits</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("#### 🚨 Critical Overdraft Accounts Flagged for Credit Committee Review")
    df_breaches = pd.DataFrame(breaches)
    st.dataframe(
        df_breaches[["severity", "distributor_id", "distributor_name", "territory", "currency", "credit_limit", "outstanding", "overdraft", "utilization_pct", "overdue_90_plus", "disputed"]],
        use_container_width=True
    )
