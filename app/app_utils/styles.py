import streamlit as st

def inject_custom_css():
    """Inject custom dark mode, glassmorphic CSS styling."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main application radial gradient background */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(243, 249, 245, 0.85) 0%, rgba(255, 255, 255, 1) 90%) !important;
    }
    
    /* Hide default Streamlit header to prevent clipping content */
    [data-testid="stHeader"], header {
        display: none !important;
    }
    
    /* Safely space top padding to avoid any clipping or overlap */
    .block-container, .stMainBlockContainer {
        padding-top: 4.5rem !important;
    }
    
    /* Dark mode forestry sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #143e21 0%, #0c1810 100%) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #f1f5f9 !important;
    }
    
    /* Input and dropdown container stylings in sidebar to prevent white-on-white text */
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background-color: #0c1c11 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="input"] > div {
        background-color: transparent !important;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #ffffff !important;
        background-color: transparent !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    [data-testid="stSidebar"] svg {
        fill: #ffffff !important;
    }
    
    /* File uploader button styling (Make it Green) */
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #1e5233 0%, #34a853 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.4rem 1.25rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }
    [data-testid="stFileUploader"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 12px rgba(52, 168, 83, 0.35) !important;
    }
    
    /* Form and action button overrides */
    div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #1e5233 0%, #34a853 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        width: 100% !important;
    }
    div.stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(52, 168, 83, 0.3) !important;
    }
    div.stFormSubmitButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Standard buttons (simulations, etc.) */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
        border: 1px solid #cbd5e1 !important;
        background-color: white !important;
        color: #1e293b !important;
    }
    div.stButton > button:hover {
        transform: translateY(-1px) !important;
        border-color: #34a853 !important;
        color: #34a853 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    }
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Sticky Header Container Parent */
    div[data-testid="stElementContainer"]:has(div.sticky-header) {
        position: -webkit-sticky;
        position: sticky;
        top: 2.875rem;
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        z-index: 999 !important;
        padding: 0.75rem 0 !important;
        margin-top: -1.5rem !important;
        border-bottom: 1px solid rgba(226, 232, 240, 0.8) !important;
        margin-bottom: 0px !important;
    }
    
    .sticky-header {
        background: transparent !important;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e5233 0%, #34a853 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    
    .tagline {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
        font-weight: 300;
    }
    
    /* Card design */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        padding: 1.25rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.25s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.03);
        border-color: #34a853;
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Agent Node & Color Coding CSS */
    .agent-node {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.25rem 0;
        border: 1px solid rgba(0,0,0,0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .agent-inactive { border-left: 5px solid #cbd5e1; background-color: #f8fafc; color: #64748b; }
    
    /* Specific Agent Colors */
    .badge-coordinator { border-left: 5px solid #64748b; background-color: #f1f5f9; color: #475569; }
    .badge-crop_doctor { border-left: 5px solid #22c55e; background-color: #f0fdf4; color: #166534; }
    .badge-weather { border-left: 5px solid #3b82f6; background-color: #eff6ff; color: #1d4ed8; }
    .badge-market { border-left: 5px solid #f97316; background-color: #fff7ed; color: #c2410c; }
    .badge-planner { border-left: 5px solid #a855f7; background-color: #faf5ff; color: #6b21a8; }
    .badge-fertilizer { border-left: 5px solid #eab308; background-color: #fefce8; color: #854d0e; }
    .badge-irrigation { border-left: 5px solid #3b82f6; background-color: #eff6ff; color: #1d4ed8; }
    .badge-government { border-left: 5px solid #06b6d4; background-color: #ecfeff; color: #0891b2; }
    
    /* Trajectory arrow */
    .trajectory-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        margin: 0.2rem 0;
        font-size: 0.85rem;
    }
    
    /* Skill pill */
    .skill-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.6rem;
        background-color: #f1f5f9;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #475569;
        border: 1px solid #e2e8f0;
        margin: 0.15rem;
    }
    
    .skill-active { background-color: #e0f2fe; color: #0369a1; border-color: #bae6fd; }

    /* Timeline visual flow */
    .timeline-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8fafc;
        padding: 0.75rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-top: 0.5rem;
        overflow-x: auto;
    }
    
    .timeline-node {
        text-align: center;
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        background: white;
        border: 1px solid #e2e8f0;
        min-width: 90px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .timeline-node.active {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        border-color: #86efac;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);
        transform: translateY(-2px) scale(1.05);
    }

    .timeline-arrow {
        color: #cbd5e1;
        font-weight: bold;
        font-size: 0.95rem;
    }

    /* Metrics panel formatting */
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f766e;
    }
    
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
    }
    
    .chat-bubble {
        padding: 1rem 1.25rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.01), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
        line-height: 1.6;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1e293b;
        border-color: #e2e8f0;
        border-bottom-right-radius: 4px;
    }
    
    .agent-bubble {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        color: #14532d;
        border-color: #bbf7d0;
        border-bottom-left-radius: 4px;
    }

    .terminal-loader {
        padding: 12px 16px;
        background-color: #0f172a;
        color: #38bdf8;
        border-left: 5px solid #38bdf8;
        border-radius: 8px;
        font-family: 'Outfit', 'Courier New', Courier, monospace;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .hitl-alert {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 5px solid #d97706;
    }

    .pulse {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 1);
        margin-right: 8px;
        animation: pulse-animation 2s infinite;
    }

    @keyframes pulse-animation {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 8px rgba(34, 197, 94, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
        }
    }

    /* Style Streamlit Tabs active state to be green instead of red */
    button[data-baseweb="tab"] {
        color: #64748b !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #34a853 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #34a853 !important;
        border-bottom-color: #34a853 !important;
    }

    /* Override focus borders and selection rings of input elements */
    [data-testid="stSidebar"] div[data-baseweb="input"]:focus-within,
    [data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
        border-color: #34a853 !important;
    }
</style>
""", unsafe_allow_html=True)
