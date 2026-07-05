import streamlit as st

def inject_custom_css():
    """Inject custom dark mode, glassmorphic CSS styling."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
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
    .badge-crop_doctor { border-left: 5px solid #22c55e; background-color: #hn0fdf4; color: #166534; background-color: #f0fdf4; }
    .badge-weather { border-left: 5px solid #3b82f6; background-color: #eff6ff; color: #1d4ed8; }
    .badge-market { border-left: 5px solid #f97316; background-color: #fff7ed; color: #c2410c; }
    .badge-planner { border-left: 5px solid #a855f7; background-color: #faf5ff; color: #6b21a8; }
    .badge-fertilizer { border-left: 5px solid #eab308; background-color: #fefce8; color: #854d0e; }
    .badge-irrigation { border-left: 5px solid #3b82f6; background-color: #eff6ff; color: #1d4ed8; }
    
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
        font-size: 0.8rem;
        font-weight: 600;
        color: #475569;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        background: white;
        border: 1px solid #e2e8f0;
        min-width: 65px;
    }
    
    .timeline-node.active {
        background: #dcfce7;
        color: #15803d;
        border-color: #bbf7d0;
    }

    .timeline-arrow {
        color: #cbd5e1;
        font-weight: bold;
        font-size: 0.9rem;
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
        padding: 1rem 1.2rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        line-height: 1.6;
    }
    
    .user-bubble {
        background-color: #f1f5f9;
        color: #1e293b;
        border-bottom-right-radius: 4px;
    }
    
    .agent-bubble {
        background-color: #f0fdf4;
        color: #0f5132;
        border: 1px solid #d1e7dd;
        border-bottom-left-radius: 4px;
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
</style>
""", unsafe_allow_html=True)
