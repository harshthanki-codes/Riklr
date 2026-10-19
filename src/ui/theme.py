"""
Production-Grade Enterprise UI Stylesheet (Palantir Foundry / Snowflake Horizon Aesthetic)
Clean dark theme, glassmorphism cards, refined typography, crisp borders, and status pill badges.
"""

CUSTOM_CSS = """
<style>
    /* Global Background and Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main App Background */
    .stApp {
        background-color: #0B0E14;
        color: #E6EDF3;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111622 !important;
        border-right: 1px solid #1E2638;
    }

    /* Enterprise Metric Card */
    .metric-card {
        background: linear-gradient(145deg, #161D2B, #111622);
        border: 1px solid #232D42;
        border-radius: 10px;
        padding: 18px 22px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .metric-card:hover {
        border-color: #388BFD;
        transform: translateY(-2px);
    }
    .metric-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8B949E;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-delta {
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 6px;
    }
    .metric-delta.positive { color: #3FB950; }
    .metric-delta.negative { color: #F85149; }
    .metric-delta.neutral { color: #8B949E; }

    /* Pill Badges */
    .pill-badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        margin-right: 6px;
    }
    .badge-primary { background: rgba(56, 139, 253, 0.15); color: #58A6FF; border: 1px solid rgba(56, 139, 253, 0.3); }
    .badge-success { background: rgba(63, 185, 80, 0.15); color: #3FB950; border: 1px solid rgba(63, 185, 80, 0.3); }
    .badge-warning { background: rgba(210, 153, 34, 0.15); color: #D29922; border: 1px solid rgba(210, 153, 34, 0.3); }
    .badge-danger { background: rgba(248, 81, 73, 0.15); color: #F85149; border: 1px solid rgba(248, 81, 73, 0.3); }

    /* Glassmorphism Trust Footer */
    .trust-footer {
        background: #111622;
        border: 1px solid #232D42;
        border-left: 4px solid #388BFD;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 16px 0;
    }

    /* Tab bar refinement */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #1E2638;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        background-color: transparent;
        border-radius: 6px 6px 0 0;
        color: #8B949E;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #161D2B !important;
        color: #58A6FF !important;
        border: 1px solid #232D42 !important;
        border-bottom: 2px solid #388BFD !important;
    }

    /* Buttons */
    button[kind="primary"], .stButton>button {
        background: #1F6FEB !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background: #388BFD !important;
        box-shadow: 0 0 12px rgba(56, 139, 253, 0.4) !important;
    }
</style>
"""
