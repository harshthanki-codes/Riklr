"""
Production-Grade Enterprise Design System & Stylesheet
Aesthetic: Palantir Foundry / Snowflake Horizon / Linear / Stripe Terminal.
Deep dark canvas, glassmorphism frosted surfaces, high-contrast typography, and live telemetry pulses.
"""

CUSTOM_CSS = """
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Canvas */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.01em;
    }

    .stApp {
        background: radial-gradient(circle at top right, #121A2D 0%, #0A0D14 55%, #07090E 100%) !important;
        color: #E6EDF3;
    }

    /* Sidebar Refinement */
    section[data-testid="stSidebar"] {
        background: #0D121D !important;
        border-right: 1px solid #1E2638 !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
    }

    /* Pulse Dot Animation for Live Telemetry */
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #3FB950;
        box-shadow: 0 0 0 0 rgba(63, 185, 80, 0.7);
        animation: pulse 1.8s infinite;
        margin-right: 6px;
    }
    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(63, 185, 80, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 6px rgba(63, 185, 80, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(63, 185, 80, 0);
        }
    }

    /* Top Command HUD Bar */
    .command-hud {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid #1F2A3F;
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    }
    .hud-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .hud-telemetry {
        display: flex;
        align-items: center;
        gap: 16px;
        font-size: 0.8rem;
        color: #8B949E;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Enterprise Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, rgba(22, 30, 46, 0.8), rgba(14, 20, 32, 0.9));
        backdrop-filter: blur(8px);
        border: 1px solid #23304A;
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        border-color: #388BFD;
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(56, 139, 253, 0.15);
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(56, 139, 253, 0.6), transparent);
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-title {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8B949E;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.95rem;
        font-weight: 700;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.02em;
    }
    .metric-delta {
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .metric-delta.positive { color: #3FB950; }
    .metric-delta.negative { color: #F85149; }
    .metric-delta.neutral { color: #8B949E; }
    .metric-delta.warning { color: #D29922; }

    /* Pill Badges */
    .pill-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.74rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.02em;
    }
    .badge-primary { background: rgba(56, 139, 253, 0.15); color: #58A6FF; border: 1px solid rgba(56, 139, 253, 0.35); }
    .badge-success { background: rgba(63, 185, 80, 0.15); color: #3FB950; border: 1px solid rgba(63, 185, 80, 0.35); }
    .badge-warning { background: rgba(210, 153, 34, 0.15); color: #E3B341; border: 1px solid rgba(210, 153, 34, 0.35); }
    .badge-danger  { background: rgba(248, 81, 73, 0.15); color: #F85149; border: 1px solid rgba(248, 81, 73, 0.35); }
    .badge-purple  { background: rgba(163, 113, 247, 0.15); color: #BC8CFF; border: 1px solid rgba(163, 113, 247, 0.35); }

    /* Trust Governance Receipt Box */
    .trust-footer {
        background: #0E1422;
        border: 1px solid #1F2A3F;
        border-left: 4px solid #388BFD;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    /* Refined Tab Navigation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: transparent;
        border-bottom: 1px solid #1F2A3F;
        padding-bottom: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: #8B949E;
        font-weight: 500;
        font-size: 0.92rem;
        transition: color 0.15s ease, background-color 0.15s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #C9D1D9;
        background-color: rgba(255, 255, 255, 0.03);
    }
    .stTabs [aria-selected="true"] {
        background-color: #141C2C !important;
        color: #58A6FF !important;
        font-weight: 600 !important;
        border: 1px solid #23304A !important;
        border-bottom: 2px solid #388BFD !important;
    }

    /* Action Suggestion Chips */
    .action-chip {
        display: inline-block;
        background: #141C2C;
        border: 1px solid #23304A;
        border-radius: 6px;
        padding: 6px 12px;
        margin: 4px 6px 4px 0;
        font-size: 0.8rem;
        color: #C9D1D9;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .action-chip:hover {
        background: #1E283D;
        border-color: #388BFD;
        color: #58A6FF;
    }

    /* Modern Table & Dataframe */
    [data-testid="stDataFrame"], .stTable {
        border: 1px solid #1F2A3F;
        border-radius: 10px;
        overflow: hidden;
    }

    /* Button Enhancements */
    button[kind="primary"], .stButton>button {
        background: linear-gradient(180deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 8px 18px !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background: linear-gradient(180deg, #3B82F6 0%, #2563EB 100%) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* Section Subtitle Bar */
    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 12px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #1F2A3F;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-caption {
        font-size: 0.85rem;
        color: #8B949E;
    }
</style>
"""

# Plotly Enterprise Dark Theme Template
PLOTLY_DARK_THEME = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": "#C9D1D9", "size": 12},
        "xaxis": {
            "gridcolor": "#1F2A3F",
            "linecolor": "#1F2A3F",
            "zerolinecolor": "#1F2A3F",
            "tickfont": {"color": "#8B949E"}
        },
        "yaxis": {
            "gridcolor": "#1F2A3F",
            "linecolor": "#1F2A3F",
            "zerolinecolor": "#1F2A3F",
            "tickfont": {"color": "#8B949E"}
        },
        "margin": {"l": 40, "r": 20, "t": 40, "b": 40}
    }
}
