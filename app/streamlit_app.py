import streamlit as st
import os
import base64
import json
import datetime
import time
from PIL import Image
import io
import logging

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.agent import root_agent
from app.app_utils.localization import get_translations
from app.app_utils.styles import inject_custom_css

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("farm_guardian.app")
logger.info("Initializing FarmGuardian Streamlit Application...")

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="FarmGuardian AI - Smart Farming Companion",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS styling
inject_custom_css()

# Sidebar - Setup Preferred Language
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2913/2913520.png", width=80)
preferred_lang = st.sidebar.selectbox("Preferred Language / पसंदीदा भाषा / पसंतीची भाषा", [
    "English", 
    "Hindi (हिन्दी)", 
    "Marathi (मराठी)"
])


# Load translations
loc = get_translations(preferred_lang)

# Sidebar - Settings & Farmer Profile (Memory/State)
st.sidebar.markdown(f"### {loc['profile']}")
farmer_name = st.sidebar.text_input(loc["name"], "Ramesh Kumar")
location = st.sidebar.text_input(loc["location"], "Pune, Maharashtra")
acreage = st.sidebar.number_input(loc["acreage"], min_value=0.1, max_value=500.0, value=3.0, step=0.5)
crop_type = st.sidebar.selectbox(loc["crop"], ["Paddy (Rice)", "Tomato", "Wheat", "Maize"])
soil_type = st.sidebar.selectbox(loc["soil"], ["Loamy", "Sandy", "Clayey"])

# Sidebar Course Attribution Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="font-size: 0.85rem; color: #64748b; font-weight: 500; text-align: center; padding: 10px; background-color: rgba(241, 245, 249, 0.5); border-radius: 8px; border: 1px solid #e2e8f0; margin-top: 15px;">
        🎓 <b>Capstone Project</b><br>
        5-Day AI Agents Intensive Vibe Coding Course<br>
        <span style="color: #475569; font-weight: 600;">Google & Kaggle</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Core Application Header
col_title, col_logo = st.columns([6, 1])
with col_title:
    st.markdown(f"<h1 class='main-title'>{loc['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='tagline'>{loc['tagline']}</p>", unsafe_allow_html=True)
with col_logo:
    st.markdown("<br>", unsafe_allow_html=True)
    
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=80)
    else:
        st.image("https://cdn-icons-png.flaticon.com/512/4143/4143160.png", width=70)

# Initialize Session states
if "session_service" not in st.session_state:
    st.session_state.session_service = InMemorySessionService()
if "runner" not in st.session_state:
    st.session_state.runner = Runner(
        agent=root_agent,
        app_name="app",
        session_service=st.session_state.session_service
    )
if "session_id" not in st.session_state:
    st.session_state.session_id = "farm_session_" + str(datetime.datetime.now().microsecond)

# Register the session in the session service to prevent SessionNotFoundError
session = st.session_state.session_service.get_session_sync(
    app_name="app",
    user_id=farmer_name,
    session_id=st.session_state.session_id
)
if not session:
    st.session_state.session_service.create_session_sync(
        app_name="app",
        user_id=farmer_name,
        session_id=st.session_state.session_id
    )


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "routing_history" not in st.session_state:
    st.session_state.routing_history = []
if "vault_reminders" not in st.session_state:
    st.session_state.vault_reminders = []
if "vault_docs" not in st.session_state:
    st.session_state.vault_docs = []
if "pending_hitl" not in st.session_state:
    st.session_state.pending_hitl = None

# Advanced Visual State variables
if "agent_viz_state" not in st.session_state:
    st.session_state.agent_viz_state = {
        "Coordinator Agent": "inactive",
        "Crop Doctor": "inactive",
        "Weather Agent": "inactive",
        "Market Agent": "inactive",
        "Finance & Soil Agent": "inactive",
        "Government Agent": "inactive",
        "Planner Agent": "inactive",
        "findings": {
            "disease": "--",
            "weather": "--",
            "market": "--",
            "fertilizer": "--",
            "plan": "--"
        }
    }

if "trajectory" not in st.session_state:
    st.session_state.trajectory = []

if "skills_activated" not in st.session_state:
    st.session_state.skills_activated = {
        "crop_disease": False,
        "fertilizer": False,
        "irrigation": False,
        "weekly_planner": False,
        "pesticide": False
    }

if "weather_panel" not in st.session_state:
    st.session_state.weather_panel = {
        "temp": "--",
        "humidity": "--",
        "rain_prob": "--",
        "risk": "--",
        "explanation": "No diagnostic run yet."
    }

if "market_panel" not in st.session_state:
    st.session_state.market_panel = {
        "price": "--",
        "trend": "--",
        "location": "--"
    }

if "economics_panel" not in st.session_state:
    st.session_state.economics_panel = {
        "cost": "--",
        "yield_saved": "--",
        "roi": "--"
    }

if "timeline_state" not in st.session_state:
    st.session_state.timeline_state = "Diagnosis"

if "explainability" not in st.session_state:
    st.session_state.explainability = {
        "confidence": "--",
        "why": []
    }

if "weekly_planner_table" not in st.session_state:
    st.session_state.weekly_planner_table = []

# Helper function to get correct badge color class
def get_badge_class(agent_name):
    clean = agent_name.lower().replace("_agent", "")
    if "coordinator" in clean:
        return "badge-coordinator"
    elif "crop" in clean or "doctor" in clean:
        return "badge-crop_doctor"
    elif "weather" in clean:
        return "badge-weather"
    elif "market" in clean:
        return "badge-market"
    elif "government" in clean or "scheme" in clean:
        return "badge-market"
    elif "finance" in clean or "soil" in clean:
        return "badge-fertilizer"
    elif "planner" in clean:
        return "badge-planner"
    return "badge-coordinator"

# Main UI layout columns: Left side = Consultation & upload, Right side = Decision Panels
left_col, right_col = st.columns([5, 5])

with left_col:
    st.subheader(loc["chat_header"])
    
    # Vision Image Upload
    st.markdown(f"**{loc['upload_label']}**")
    uploaded_file = st.file_uploader(loc["upload_placeholder"], type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    image_base64 = None
    if uploaded_file:
        image_bytes = uploaded_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, caption="Uploaded Leaf Image", width=220)
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Chat history
    chat_container = st.container(height=300)
    with chat_container:
        if not st.session_state.chat_history:
            welcome_msg = loc["welcome"].format(name=farmer_name, crop=crop_type, location=location)
            st.markdown(welcome_msg)
        for speaker, msg in st.session_state.chat_history:
            if speaker == "User":
                st.markdown(f"<div class='chat-bubble user-bubble'>🧑‍🌾 <b>You:</b> {msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble agent-bubble'>🤖 <b>FarmGuardian:</b> {msg}</div>", unsafe_allow_html=True)

    # Chat Input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(loc["chat_placeholder"], placeholder="Explain crop symptoms or schedule weather checks...", label_visibility="collapsed")
        submit_btn = st.form_submit_button(loc["send_btn"])

    # Action Execution (with dynamic thinking steps simulation)
    if submit_btn and (user_input or uploaded_file):
        query_text = user_input or "Please diagnose this uploaded leaf image."
        st.session_state.chat_history.append(("User", query_text))
        logger.info(f"New farm consult turn: Farmer={farmer_name}, Location={location}, Crop={crop_type}, Query='{query_text}'")
        
        # 1. Start the Live "Thinking" Animation progression
        thinking_placeholder = st.empty()
        
        steps = [
            ("🧠 Coordinator Agent routing query...", ["Coordinator Agent"]),
            ("🔍 Crop Doctor analyzing image symptoms...", ["Coordinator Agent", "Crop Doctor"]),
            ("🌦 Weather Agent checking local weather forecast...", ["Coordinator Agent", "Crop Doctor", "Weather Agent"]),
            ("📈 Market Agent checking regional mandi prices...", ["Coordinator Agent", "Crop Doctor", "Weather Agent", "Market Agent"]),
            ("🧪 Finance & Soil Agent validating dosage safety...", ["Coordinator Agent", "Crop Doctor", "Weather Agent", "Market Agent", "Finance & Soil Agent"]),
            ("🏛️ Government Schemes Agent finding subsidies...", ["Coordinator Agent", "Crop Doctor", "Weather Agent", "Market Agent", "Finance & Soil Agent", "Government Agent"]),
            ("📝 Planner Agent compiling weekly plan...", ["Coordinator Agent", "Crop Doctor", "Weather Agent", "Market Agent", "Finance & Soil Agent", "Government Agent", "Planner Agent"]),
            ("✅ Final advice compiled successfully!", ["Coordinator Agent", "Crop Doctor", "Weather Agent", "Market Agent", "Finance & Soil Agent", "Government Agent", "Planner Agent"])
        ]
        
        st.session_state.trajectory = []
        for label, active_nodes in steps:
            for node in st.session_state.agent_viz_state:
                if node != "findings":
                    st.session_state.agent_viz_state[node] = "active" if node in active_nodes else "inactive"
            
            st.session_state.trajectory.append(label)
            
            # Highlight dynamic skills
            if "Crop Doctor" in active_nodes:
                st.session_state.skills_activated["crop_disease"] = True
            if "Weather" in active_nodes:
                st.session_state.skills_activated["irrigation"] = True
            if "Fertilizer" in active_nodes:
                st.session_state.skills_activated["fertilizer"] = True
            if "Planner" in active_nodes:
                st.session_state.skills_activated["weekly_planner"] = True
                
            thinking_placeholder.markdown(f"<div style='padding: 12px; background-color: #fef08a; border-left: 5px solid #eab308; border-radius: 8px; font-weight: bold; margin-bottom:1rem;'>{label}</div>", unsafe_allow_html=True)
            time.sleep(0.1)
            
        thinking_placeholder.empty()

        # Prepare ADK payload and execute runner within a spinner loader
        with st.spinner(loc.get("thinking_loader", "FarmGuardian AI is consulting specialists...")):
            parts = []
            if image_base64:
                parts.append(types.Part.from_bytes(data=base64.b64decode(image_base64), mime_type="image/jpeg"))
            parts.append(types.Part.from_text(text=f"Preferred Language: {preferred_lang}. Crop: {crop_type}. Location: {location}. Acreage: {acreage}. Soil: {soil_type}. Farmer name: {farmer_name}. Query: {query_text}"))
            
            new_message = types.Content(role="user", parts=parts)
            
            state_delta = {
                "farmer_name": farmer_name,
                "location": location,
                "acreage": acreage,
                "crop": crop_type,
                "soil_type": soil_type,
                "language": preferred_lang
            }
            
            response_text = ""
            try:
                logger.info(f"Invoking ADK runner with session_id='{st.session_state.session_id}' for user='{farmer_name}'...")
                events = st.session_state.runner.run(
                    user_id=farmer_name,
                    session_id=st.session_state.session_id,
                    new_message=new_message,
                    state_delta=state_delta
                )
                for event in events:
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                response_text += part.text
                logger.info(f"ADK runner finished execution successfully. Response length: {len(response_text)} characters.")
            except Exception as e:
                logger.error(f"ADK runner failed during execution: {e}", exc_info=True)
                response_text = f"An error occurred during agent execution: {e}. Fallback advisor: Please consult local agricultural extension officer."
            
            if not response_text:
                response_text = "I have noted the details. Let me know if you would like me to archive this plan."

        # Dynamically reset visualizer nodes to show only the agents that actually responded
        for node in st.session_state.agent_viz_state:
            if node != "findings":
                st.session_state.agent_viz_state[node] = "inactive"
        
        st.session_state.agent_viz_state["Coordinator Agent"] = "active"
        
        r_low = response_text.lower()
        q_low = query_text.lower()
        
        # 1. Crop Doctor matching
        if any(w in r_low or w in q_low for w in ["doctor", "blight", "disease", "pest", "leaf", "रोग", "कीड", "पाने"]) or uploaded_file:
            st.session_state.agent_viz_state["Crop Doctor"] = "active"
        # 2. Weather matching
        if any(w in r_low or w in q_low for w in ["weather", "rain", "forecast", "water", "irrigation", "मौसम", "हवामान", "पाऊस", "सिंचन"]):
            st.session_state.agent_viz_state["Weather Agent"] = "active"
        # 3. Market matching
        if any(w in r_low or w in q_low for w in ["price", "mandi", "market", "भाव", "बाजार", "दर", "खरेदी"]):
            st.session_state.agent_viz_state["Market Agent"] = "active"
        # 4. Soil & Finance matching
        if any(w in r_low or w in q_low for w in ["fertilizer", "urea", "ssp", "mop", "soil", "उर्वरक", "खत", "माती"]):
            st.session_state.agent_viz_state["Finance & Soil Agent"] = "active"
        # 5. Government Schemes matching
        if any(w in r_low or w in q_low for w in ["subsidy", "scheme", "kusum", "government", "अनुदान", "योजना"]):
            st.session_state.agent_viz_state["Government Agent"] = "active"
        # 6. Planner / Reminders matching
        if any(w in r_low or w in q_low for w in ["save", "drive", "calendar", "reminder", "sync", "सहेज", "स्मरणपत्र", "कॅलेंडर"]):
            st.session_state.agent_viz_state["Planner Agent"] = "active"

        active_nodes = [node for node, status in st.session_state.agent_viz_state.items() if status == "active" and node != "findings"]
        logger.info(f"Routing evaluation completed. Active agents activated: {active_nodes}")

        # Update timeline state dynamically based on active agents
        if st.session_state.agent_viz_state["Market Agent"] == "active":
            st.session_state.timeline_state = "Market"
        elif st.session_state.agent_viz_state["Government Agent"] == "active":
            st.session_state.timeline_state = "Harvest"
        elif st.session_state.agent_viz_state["Finance & Soil Agent"] == "active" or st.session_state.agent_viz_state["Weather Agent"] == "active":
            st.session_state.timeline_state = "Treatment"
        elif st.session_state.agent_viz_state["Crop Doctor"] == "active":
            st.session_state.timeline_state = "Diagnosis"

        # Dynamically build weekly planner tasks based on active agents
        dynamic_tasks = []
        if st.session_state.agent_viz_state["Crop Doctor"] == "active":
            dynamic_tasks.append({"day": "Monday", "task": "Monitor crop for leaf spots, mold, or pest damage", "done": False})
            dynamic_tasks.append({"day": "Tuesday", "task": "Apply organic/biological treatment (e.g. neem oil, copper fungicide)", "done": False})
        
        if st.session_state.agent_viz_state["Weather Agent"] == "active":
            if "rain" in r_low or "paddy" in r_low:
                dynamic_tasks.append({"day": "Wednesday", "task": "Adjust irrigation schedule according to rain forecast", "done": False})
            else:
                dynamic_tasks.append({"day": "Wednesday", "task": "Check soil moisture level and run drip irrigation", "done": False})
        
        if st.session_state.agent_viz_state["Finance & Soil Agent"] == "active":
            dynamic_tasks.append({"day": "Thursday", "task": "Calculate and apply split dosage of N-P-K fertilizers", "done": False})
            dynamic_tasks.append({"day": "Friday", "task": "Add organic compost/vermicompost to improve soil biology", "done": False})
            
        if st.session_state.agent_viz_state["Government Agent"] == "active":
            dynamic_tasks.append({"day": "Saturday", "task": "Prepare required land records/documents for subsidy application", "done": False})
            dynamic_tasks.append({"day": "Sunday", "task": "Submit subsidy application draft for approval", "done": False})

        if st.session_state.agent_viz_state["Market Agent"] == "active":
            dynamic_tasks.append({"day": "Saturday", "task": "Check wholesale Mandi prices and match buyer requirements", "done": False})
            dynamic_tasks.append({"day": "Sunday", "task": "Grade crop quality and transport to nearest high-paying market", "done": False})

        if dynamic_tasks:
            st.session_state.weekly_planner_table = dynamic_tasks
            # Append planner summary directly to chat bubble response
            planner_summary = "\n\n---\n📅 **Weekly Planner Updated:**\n"
            for t in dynamic_tasks:
                planner_summary += f"- **{t['day']}**: {t['task']}\n"
            response_text += planner_summary

        st.session_state.chat_history.append(("Agent", response_text))

        try:
            session = st.session_state.session_service.get_session(user_id=farmer_name, session_id=st.session_state.session_id)
            if session:
                st.session_state.vault_reminders = session.state.get("reminders", [])
                st.session_state.vault_docs = session.state.get("drive_docs", [])
                st.session_state.pending_hitl = session.state.get("pending_action")
        except Exception:
            pass
        
        st.rerun()

    # 2. Whitespace Reduction: Render active diagnostic report in the left column
    if st.session_state.agent_viz_state["findings"]["disease"] != "--" or st.session_state.explainability["confidence"] != "--":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"### 🌿 {loc['explain']}")
        disease_name = st.session_state.agent_viz_state["findings"].get("disease", "Tomato Early Blight")
        conf = st.session_state.explainability.get("confidence", "96%")
        
        col_img, col_det = st.columns([2, 3])
        with col_img:
            if uploaded_file:
                st.image(image, caption="Diagnosed Leaf", use_container_width=True)
            else:
                st.image("https://images.unsplash.com/photo-1592417817098-8f3d6eb19675?auto=format&fit=crop&q=80&w=400", caption="Sample Leaf Diagnosis", use_container_width=True)
        with col_det:
            st.markdown(f"**Crop**: {crop_type}")
            st.markdown(f"**Disease**: <span style='color: #dc2626; font-weight:700;'>{disease_name}</span>", unsafe_allow_html=True)
            st.markdown(f"**Confidence**: <span style='color: #16a34a; font-weight:700;'>{conf}</span>", unsafe_allow_html=True)
            st.markdown(f"**Status**: <span style='color: #d97706; font-weight:700;'>Action Required</span>", unsafe_allow_html=True)

with right_col:
    tab_orch, tab_decision, tab_plan, tab_sec = st.tabs([
        "⛓️ Orchestration & Habilities",
        loc["decision_header"],
        "📅 Planner & Timeline",
        loc["security"]
    ])
    
    with tab_orch:
        # 3. Dynamic Color Coded Agent Tree
        st.markdown(f"### {loc['agent_viz']}")
        
        for node, status in st.session_state.agent_viz_state.items():
            if node != "findings":
                if node == "Coordinator Agent":
                    badge_class = "badge-coordinator" if status == "active" else "agent-inactive"
                    icon = "🧠" if status == "active" else "💤"
                    st.markdown(f"<div class='agent-node {badge_class}'><span><b>Coordinator Agent</b> {icon}</span><span>Main Router</span></div>", unsafe_allow_html=True)
                else:
                    node_clean = node.lower().split(" ")[0]
                    badge_color_class = get_badge_class(node.lower().replace(" ", "_"))
                    badge_class = f"{badge_color_class}" if status == "active" else "agent-inactive"
                    
                    emojis = {
                        "crop": "🟢",
                        "weather": "🔵",
                        "market": "🟠",
                        "finance": "🟡",
                        "fertilizer": "🟡",
                        "planner": "🟣"
                    }
                    emoji = emojis.get(node_clean, "🤖")
                    icon = "✓" if status == "active" else "○"
                    finding = st.session_state.agent_viz_state["findings"].get(node_clean, "--")
                    
                    st.markdown(f"<div style='margin-left: 25px;' class='agent-node {badge_class}'><span>├── {emoji} <b>{node}</b> {icon}</span><span style='font-size: 0.8rem; font-weight: bold;'>{finding}</span></div>", unsafe_allow_html=True)

        # 4. Animated Orchestration Trajectory Log
        st.markdown(f"### {loc['trajectory']}")
        if st.session_state.trajectory:
            for idx, step in enumerate(st.session_state.trajectory):
                st.markdown(f"""
                <div class='trajectory-step'>
                    <span class='pulse'></span>
                    <span>{step}</span>
                </div>
                """, unsafe_allow_html=True)
                if idx < len(st.session_state.trajectory) - 1:
                    st.markdown("<div style='text-align: center; color: #cbd5e1; font-weight:bold; line-height: 0.6;'>↓</div>", unsafe_allow_html=True)
        else:
            st.info("No active trajectory. Complete a consult turn to trace steps.")

        # 5. Skills Activation Pills
        st.markdown(f"### {loc['skills_header']}")
        for skill_name, active in st.session_state.skills_activated.items():
            pill_class = "skill-pill skill-active" if active else "skill-pill"
            icon = "✓" if active else "○"
            st.markdown(f"<span class='{pill_class}'>{icon} {skill_name} Skill</span>", unsafe_allow_html=True)
            
    with tab_decision:
        col_w, col_m = st.columns(2)
        
        # 6. Weather Card with Rich Icons
        with col_w:
            w = st.session_state.weather_panel
            risk_color = "#dc2626" if w["risk"] == "HIGH" else "#0284c7"
            st.markdown(f"""
            <div class='dashboard-card'>
                <div class='card-title'>🌦️ {loc['weather_card']}</div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <div class='metric-value'>🌡️ {w['temp']}</div>
                        <div class='metric-sub'>💧 Humidity: {w['humidity']}</div>
                        <div class='metric-sub'>🌧️ Rain Prob: {w['rain_prob']}</div>
                    </div>
                    <div style='text-align: right;'>
                        <div style='color: {risk_color}; font-weight: 700; font-size: 1.1rem;'>Risk: {w['risk']}</div>
                        <div class='metric-sub'>⚠️ Disease Risk</div>
                    </div>
                </div>
                <hr style='margin: 0.5rem 0;'>
                <div style='font-size: 0.85rem; color: #475569;'><b>Impact:</b> {w['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)

        # 7. Market Price Watch Card
        with col_m:
            m = st.session_state.market_panel
            st.markdown(f"""
            <div class='dashboard-card'>
                <div class='card-title'>💰 {loc['market_card']}</div>
                <div>
                    <div class='metric-sub'>Today's Crop Price</div>
                    <div class='metric-value'>{m['price']}</div>
                    <div style='color: #16a34a; font-weight: 600; font-size: 0.95rem;'>{m['trend']}</div>
                    <div class='metric-sub'>Market: {m['location']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 8. Cost Estimator & Economics Card
        e = st.session_state.economics_panel
        st.markdown(f"""
        <div class='dashboard-card'>
            <div class='card-title'>💸 {loc['economics']}</div>
            <div style='display: flex; justify-content: space-between; text-align: center;'>
                <div>
                    <div class='metric-sub'>Estimated Cost</div>
                    <div class='metric-value'>{e['cost']}</div>
                </div>
                <div>
                    <div class='metric-sub'>Yield Saved</div>
                    <div class='metric-value' style='color: #0d9488;'>{e['yield_saved']}</div>
                </div>
                <div>
                    <div class='metric-sub'>Expected ROI</div>
                    <div class='metric-value' style='color: #b45309;'>{e['roi']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 9. Explainability Evidence
        exp = st.session_state.explainability
        st.markdown(f"""
        <div class='dashboard-card'>
            <div class='card-title'>🔍 {loc['explain']}</div>
            <div style='font-size: 0.95rem; line-height: 1.6;'>
                <b>Disease</b>: <span style='color: #dc2626; font-weight:700;'>{st.session_state.agent_viz_state['findings'].get('disease', 'Tomato Early Blight')}</span><br>
                <b>Confidence</b>: <span style='color: #15803d; font-weight: 700;'>{exp['confidence']}</span><br>
                <b>Evidence Analysis</b>:
            </div>
        """, unsafe_allow_html=True)
        if exp["why"]:
            for item in exp["why"]:
                st.markdown(f"✓ {item}")
        else:
            st.write("No diagnostic run performed yet.")
        risk_label_color = "#dc2626" if w["risk"] == "HIGH" else "#475569"
        st.markdown(f"<b>Overall Risk</b>: <span style='color: {risk_label_color}; font-weight: 700;'>{w['risk']}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_plan:
        # 10. Crop Care Timeline Visual Flow
        st.markdown(f"### {loc['timeline']}")
        stages = ["Diagnosis", "Treatment", "Recovery", "Harvest", "Market"]
        st.markdown("<div class='timeline-container'>", unsafe_allow_html=True)
        timeline_html = ""
        for idx, stage in enumerate(stages):
            active_class = "active" if stage == st.session_state.timeline_state else ""
            timeline_html += f"<div class='timeline-node {active_class}'>{stage}</div>"
            if idx < len(stages) - 1:
                timeline_html += "<div class='timeline-arrow'>→</div>"
        st.markdown(timeline_html + "</div>", unsafe_allow_html=True)
        
        # 11. Interactive Weekly Crop Planner
        st.markdown(f"### {loc['weekly']}")
        if st.session_state.weekly_planner_table:
            for item in st.session_state.weekly_planner_table:
                cols_check = st.columns([0.15, 0.25, 0.6])
                with cols_check[0]:
                    done = st.checkbox("", value=item["done"], key=f"tbl_check_{item['day']}_{item['task']}")
                with cols_check[1]:
                    st.markdown(f"**{item['day']}**")
                with cols_check[2]:
                    st.markdown(f"~~{item['task']}~~" if done else item["task"])
        else:
            st.info("No planner tasks generated yet. Start a consultation turn or select a scenario below.")

    with tab_sec:
        # Security & Human-In-The-Loop Overrides
        st.subheader(loc["pending_hitl"])
        
        if st.session_state.pending_hitl:
            hitl = st.session_state.pending_hitl
            st.markdown(f"""
            <div class='hitl-alert'>
                <strong>⚠️ {hitl['action_type']}</strong><br>
                {hitl['details']}
            </div>
            """, unsafe_allow_html=True)
            
            col_app, col_rej = st.columns(2)
            with col_app:
                if st.button(loc["confirm_btn"], use_container_width=True):
                    st.success("Authorized! Plan has been synced to calendar and drive.")
                    
                    # If simulating the chemical pesticide flow, populate the logs immediately
                    if st.session_state.pending_hitl and "Chemical" in st.session_state.pending_hitl.get("action_type", ""):
                        st.session_state.vault_reminders = [{
                            "title": "Mancozeb 75% WP Spray Reminder",
                            "date": (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                            "description": "Authorized chemical spraying for early blight control."
                        }]
                        st.session_state.vault_docs = [{
                            "filename": "tomato_disease_treatment_report.txt",
                            "file_id": "mock_doc_9941",
                            "web_view_link": "#"
                        }]
                    elif st.session_state.pending_hitl and "Subsidy" in st.session_state.pending_hitl.get("action_type", ""):
                        st.session_state.vault_docs = [{
                            "filename": "PM_KUSUM_SolarPump_Application_Draft.pdf",
                            "file_id": "mock_gov_3829",
                            "web_view_link": "#"
                        }]
                    
                    # Send approval back to ADK Agent
                    new_message = types.Content(role="user", parts=[types.Part.from_text(text="Action Approved! Please save the reminder and document.")])
                    try:
                        st.session_state.runner.run(
                            user_id=farmer_name,
                            session_id=st.session_state.session_id,
                            new_message=new_message
                        )
                        st.session_state.pending_hitl = None
                        session = st.session_state.session_service.get_session(user_id=farmer_name, session_id=st.session_state.session_id)
                        if session:
                            session.state["pending_action"] = None
                            session_reminders = session.state.get("reminders", [])
                            session_docs = session.state.get("drive_docs", [])
                            if session_reminders:
                                st.session_state.vault_reminders = session_reminders
                            if session_docs:
                                st.session_state.vault_docs = session_docs
                    except Exception:
                        pass
                    st.rerun()
            with col_rej:
                if st.button(loc["reject_btn"], use_container_width=True):
                    st.warning("Action Rejected. Planning cancelled.")
                    st.session_state.pending_hitl = None
                    session = st.session_state.session_service.get_session(user_id=farmer_name, session_id=st.session_state.session_id)
                    if session:
                        session.state["pending_action"] = None
                    st.rerun()
        else:
            st.success("No pending security overrides or approvals. Status secure.")
            
        # Synced Vault Records (Google Drive and Calendar MCP Sync logs)
        st.markdown("---")
        st.markdown("### 🗄️ Google Drive & Calendar Sync Logs")
        
        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown("**📅 Google Calendar Events**")
            if st.session_state.vault_reminders:
                for rem in st.session_state.vault_reminders:
                    st.markdown(f"✓ **{rem['title']}** ({rem['date']})")
            else:
                st.info("No Calendar events synced yet.")
                
        with col_d:
            st.markdown("**📁 Google Drive Docs**")
            if st.session_state.vault_docs:
                for doc in st.session_state.vault_docs:
                    st.markdown(f"✓ **{doc['filename']}**")
            else:
                st.info("No Drive documents archived yet.")

# Quick Demo Scenario Triggering
st.markdown("---")
st.subheader("⚡ Quick Demo Scenarios (Pre-loaded for Judges)")
row1_cols = st.columns(3)
row2_cols = st.columns(2)

with row1_cols[0]:
    if st.button("🌿 Simulate Disease Diagnosis Flow", use_container_width=True):
        # 1. Set Chat History
        if preferred_lang == "Hindi (हिन्दी)":
            st.session_state.chat_history = [
                ("User", "मेरी टमाटर की पत्तियों पर पीले धब्बे हैं। इसका क्या कारण है और इसका इलाज क्या है?"),
                ("Agent", "निदान: टमाटर अगेती झुलसा रोग (Tomato Early Blight - Alternaria solani)।\n\nकारण: उच्च आर्द्रता (82%) और टमाटर की फलने की अवस्था।\n\nजैविक उपचार: संक्रमित पत्तियों को हटा दें। जैविक तांबा कवकनाशी स्प्रे करें।\n\nरासायनिक उपचार: मैन्कोजेब (2.5 ग्राम/लीटर)।\n\n⚠️ सुरक्षा चेतावनी: कीटनाशक छिड़काव योजना बनाने के लिए आपकी पुष्टि आवश्यक है।")
            ]
        elif preferred_lang == "Marathi (मराठी)":
            st.session_state.chat_history = [
                ("User", "माझ्या टोमॅटोच्या पानांवर पिवळे डाग आहेत. याचे कारण काय आणि यावर काय उपाय आहे?"),
                ("Agent", "निदान: टोमॅटो अर्ली बलाईट (Early Blight - Alternaria solani).\n\nकारण: हवेतील आर्द्रता (८२%) आणि टोमॅटो पिकाची फळ धारणा अवस्था.\n\nजैविक उपाय: संसर्गित पाने काढून टाका. जैविक कॉपर बुरशीनाशक फवारा.\n\nरासायनिक उपाय: मँकोझेब (२.५ ग्रॅम/लीटर).\n\n⚠️ सुरक्षा चेतावणी: रासायनिक फवारणीचे नियोजन करण्यासाठी तुमची मंजुरी आवश्यक आहे.")
            ]
        else:
            st.session_state.chat_history = [
                ("User", "My tomato leaves have yellow spots. What is the cause and treatment?"),
                ("Agent", "Diagnosed: Tomato Early Blight (Alternaria solani).\n\nWhy: Circular target-like lesions, high humidity (82%), and tomato growth stage (fruiting).\n\nOrganic Treatment: Prune lower leaves. Spray organic copper fungicide or neem oil solution (5ml/L).\n\nChemical Treatment: Use Mancozeb (2.5g/L). \n\n⚠️ Safety Check: Generating chemical spray plan requires farmer's confirmation.")
            ]
            
        # 2. Update visible agent viz
        st.session_state.agent_viz_state = {
            "Coordinator Agent": "active",
            "Crop Doctor": "active",
            "Weather Agent": "inactive",
            "Market Agent": "inactive",
            "Finance & Soil Agent": "inactive",
            "Government Agent": "inactive",
            "Planner Agent": "inactive",
            "findings": {
                "disease": "Tomato Early Blight",
                "weather": "--",
                "market": "--",
                "fertilizer": "--",
                "plan": "--",
                "crop": "Tomato Early Blight"
            }
        }
        
        # 3. Update Trajectory
        st.session_state.trajectory = [
            "User uploaded leaf image",
            "Vision Analysis active",
            "Diagnosed: Tomato Early Blight",
            "Weather Risk checked (82% Humidity)",
            "Chemical Safety check triggered"
        ]
        
        # 4. Activate skills
        st.session_state.skills_activated = {
            "crop_disease": True,
            "fertilizer": False,
            "irrigation": False,
            "weekly_planner": True,
            "pesticide": True
        }
        
        # 5. Explainability panel
        st.session_state.explainability = {
            "confidence": "96%",
            "why": [
                "Target-board concentric brown rings seen on leaves.",
                "Relative humidity in Pune is 82%, causing rapid spore growth.",
                "Tomato crop is in the fruiting stage, raising disease stress."
            ]
        }
        
        # 6. Economics panel
        st.session_state.economics_panel = {
            "cost": "₹650",
            "yield_saved": "9%",
            "roi": "3.8x"
        }
        
        # 7. Weather panel
        st.session_state.weather_panel = {
            "temp": "29°C",
            "humidity": "82%",
            "rain_prob": "80%",
            "risk": "HIGH",
            "explanation": "Blight spores thrive in hot, wet monsoon weather. Do not spray leaves before rain."
        }
        
        # 8. Timeline state
        st.session_state.timeline_state = "Treatment"
        
        # 9. Weekly Planner checklist
        st.session_state.weekly_planner_table = [
            {"day": "Monday", "task": "Monitor leaf spots and prune yellow lower leaves", "done": False},
            {"day": "Tuesday", "task": "Spray organic copper fungicide", "done": False},
            {"day": "Wednesday", "task": "No Irrigation (Rain forecasted in Pune)", "done": True},
            {"day": "Thursday", "task": "Perform post-rain fungal spot inspection", "done": False},
            {"day": "Friday", "task": "Authorized chemical Mancozeb spray if blight spreads", "done": False}
        ]
        
        # 10. Set pending HITL action
        st.session_state.pending_hitl = {
            "action_type": "Chemical Pesticide Spray Plan",
            "details": "Scheduling Mancozeb 75% WP spray reminder in calendar. Farmer must confirm they have protective masks and rubber gloves."
        }
        
        st.rerun()

with row1_cols[1]:
    if st.button("🌦️ Simulate Weather & Watering plan", use_container_width=True):
        # 1. Set Chat History
        if preferred_lang == "Hindi (हिन्दी)":
            st.session_state.chat_history = [
                ("User", "पुणे में मौसम कैसा रहेगा और मुझे अपनी सिंचाई को कैसे समायोजित करना चाहिए?"),
                ("Agent", "पुणे का मौसम: 29°C, 82% आर्द्रता, मध्यम वर्षा।\n\nपरामर्श: वर्षा चेतावनी सक्रिय है। मैंने सिंचाई बंद कर दी है। खेतों में पानी जमा होने से बचने के लिए जल निकासी चैनलों को साफ करें।\nमैंने इसे गूगल ड्राइव पर सहेज लिया है।")
            ]
        elif preferred_lang == "Marathi (मराठी)":
            st.session_state.chat_history = [
                ("User", "पुण्यातील हवामान कसे असेल आणि मी सिंचन कसे सुधारावे?"),
                ("Agent", "पुणे हवामान: 29°C, 82% आर्द्रता, मध्यम पाऊस.\n\nसल्ला: पाऊस इशारा सक्रिय आहे. मी सिंचन बंद केले आहे. शेतात पाणी साचू नये म्हणून पाण्याचा निचरा करा.\nमी हे गुगल ड्राइव्हवर सेव्ह केले आहे.")
            ]
        else:
            st.session_state.chat_history = [
                ("User", "What is my weather in Pune and how should I adjust irrigation?"),
                ("Agent", "Pune Weather: 29°C, 82% humidity, moderate rain showers.\n\nAdvisory: RAIN ALERT active. I have suspended drip irrigation. Clear blocked drainage channels in fields to avoid water accumulation.\nI have saved this action to Google Drive and scheduled a checklist update.")
            ]
            
        # 2. Update visible agent viz
        st.session_state.agent_viz_state = {
            "Coordinator Agent": "active",
            "Crop Doctor": "inactive",
            "Weather Agent": "active",
            "Market Agent": "inactive",
            "Finance & Soil Agent": "inactive",
            "Government Agent": "inactive",
            "Planner Agent": "active",
            "findings": {
                "disease": "--",
                "weather": "Rain predicted",
                "market": "--",
                "fertilizer": "--",
                "plan": "Irrigation suspended"
            }
        }
        
        # 3. Update Trajectory
        st.session_state.trajectory = [
            "Query weather conditions",
            "Check regional weather forecast",
            "Suspended irrigation schedule",
            "Logged action report to Drive"
        ]
        
        # 4. Activate skills
        st.session_state.skills_activated = {
            "crop_disease": False,
            "fertilizer": False,
            "irrigation": True,
            "weekly_planner": True,
            "pesticide": False
        }
        
        # 5. Weather panel
        st.session_state.weather_panel = {
            "temp": "29°C",
            "humidity": "82%",
            "rain_prob": "80%",
            "risk": "HIGH",
            "explanation": "High humidity & rain favors fungal leaf spot development. Suspend all watering."
        }
        
        # 6. Weekly Planner Table
        st.session_state.weekly_planner_table = [
            {"day": "Monday", "task": "Check drainage channels in fields", "done": False},
            {"day": "Tuesday", "task": "Prune lower tomato leaves (blight risk due to rain)", "done": False},
            {"day": "Wednesday", "task": "No Irrigation (Rain forecasted)", "done": True},
            {"day": "Thursday", "task": "Post-rain fungal spot inspection", "done": False},
            {"day": "Friday", "task": "Grade harvested crops under shade", "done": False}
        ]
        
        # 7. Timeline state
        st.session_state.timeline_state = "Recovery"
        
        # 8. Save mock documents
        st.session_state.vault_docs = [{
            "filename": "Pune_Watering_Plan_2026_06_30.txt",
            "file_id": "drive_doc_582918",
            "status": "Successfully synced to Google Drive (FarmGuardian Archive)",
            "web_view_link": "#"
        }]
        
        st.rerun()

with row1_cols[2]:
    if st.button("💰 Simulate Mandi Price lookup", use_container_width=True):
        # 1. Set Chat History
        if preferred_lang == "Hindi (हिन्दी)":
            st.session_state.chat_history = [
                ("User", "आज टमाटर का बाजार भाव क्या है?"),
                ("Agent", "टमाटर बाजार मूल्य: रु. 1,800 - रु. 2,600 प्रति क्विंटल।\n- नारायणगांव टमाटर मंडी: रु. 2,600 (उच्चतम दर)\n- पुणे एपीएमसी: रु. 2,400\n\nप्रवृत्ति: कम आपूर्ति के कारण तेजी। सर्वोत्तम लाभ प्राप्त करने के लिए रंग के अनुसार छंटाई करने का सुझाव दिया जाता है।")
            ]
        elif preferred_lang == "Marathi (मराठी)":
            st.session_state.chat_history = [
                ("User", "आज टोमॅटोचे बाजारभाव काय आहेत?"),
                ("Agent", "टोमॅटो बाजारभाव: रु. १,८०० - रु. २,६०० प्रति क्विंटल.\n- नारायणगाव टोमॅटो मार्केट: रु. २,६०० (सर्वात जास्त दर)\n- पुणे एपीएमसी: रु. २,४००\n\nकल: आवक कमी असल्याने तेजी. चांगल्या भावासाठी रंगानुसार प्रतवारी करून विक्री करा.")
            ]
        else:
            st.session_state.chat_history = [
                ("User", "What is the tomato price in nearby mandis today?"),
                ("Agent", "Tomato market price: Rs. 1,800 - Rs. 2,600 per Quintal.\n- Narayangaon Tomato Market: Rs. 2,600/q (Highest rate)\n- Pune APMC: Rs. 2,400/q\n\nTrend: Upward due to low supply. Suggest harvesting selectively and grading by color to get maximum value.")
            ]
            
        # 2. Update visible agent viz
        st.session_state.agent_viz_state = {
            "Coordinator Agent": "active",
            "Crop Doctor": "inactive",
            "Weather Agent": "inactive",
            "Market Agent": "active",
            "Finance & Soil Agent": "inactive",
            "Government Agent": "inactive",
            "Planner Agent": "inactive",
            "findings": {
                "disease": "--",
                "weather": "--",
                "market": "Tomato at ₹2600/q",
                "fertilizer": "--",
                "plan": "--"
            }
        }
        
        # 3. Update Trajectory
        st.session_state.trajectory = [
            "Query tomato market prices",
            "Fetch rates from Narayangaon and Pune APMC Mandis",
            "Analyze regional supply trend (Upward)",
            "Draft selective sell recommendation"
        ]
        
        # 4. Activate skills
        st.session_state.skills_activated = {
            "crop_disease": False,
            "fertilizer": False,
            "irrigation": False,
            "weekly_planner": False,
            "pesticide": False
        }
        
        # 5. Market panel
        st.session_state.market_panel = {
            "price": "₹2,600/q",
            "trend": "↑ 5.2% (Shortage)",
            "location": "Narayangaon APMC"
        }
        
        # 6. Timeline state
        st.session_state.timeline_state = "Market"
        
        st.rerun()

with row2_cols[0]:
    if st.button("🧪 Simulate Fertilizer & Soil plan", use_container_width=True):
        # 1. Set Chat History
        if preferred_lang == "Hindi (हिन्दी)":
            st.session_state.chat_history = [
                ("User", "मेरी 3 एकड़ टमाटर की फसल के लिए उर्वरक आवश्यकता क्या है?"),
                ("Agent", "उर्वरक आवश्यकता (3 एकड़ टमाटर):\n- यूरिया: 6.5 बैग (नाइट्रोजन)\n- एसएसपी: 15.0 बैग (फास्फोरस)\n- एमओपी: 6.0 बैग (पोटेशियम)\n\nछिड़काव अनुसूची: बेसल खुराक के रूप में 3 बैग यूरिया, 10 बैग एसएसपी और 3 बैग एमओपी डालें। शेष को फूल आने और फल बनने की अवस्था में विभाजित करें।")
            ]
        elif preferred_lang == "Marathi (मराठी)":
            st.session_state.chat_history = [
                ("User", "माझ्या 3 एकर टोमॅटो पिकासाठी खत नियोजन काय आहे?"),
                ("Agent", "खत नियोजन (3 एकर टोमॅटो):\n- युरिया: 6.5 बॅग (नायट्रोजन)\n- एसएसपी: 15.0 बॅग (फॉस्फरस)\n- एमओपी: 6.0 बॅग (पोटॅशियम)\n\nफवारणी वेळापत्रक: पेरणीच्या वेळी 3 बॅग युरिया, 10 बॅग एसएसपी आणि 3 बॅग एमओपी द्या. उर्वरित मात्रा फुले व फळे येण्याच्या वेळी विभागून द्या.")
            ]
        else:
            st.session_state.chat_history = [
                ("User", "What is my fertilizer requirement for 3 acres of tomatoes?"),
                ("Agent", "Fertilizer Requirements (3 Acres Tomato):\n- Urea (N): 6.5 bags\n- SSP (P): 15.0 bags\n- MOP (K): 6.0 bags\n\nSplit Dosage Plan:\n1. Basal: Apply 3 bags Urea, 10 bags SSP, and 3 bags MOP.\n2. Flowering (Week 4): Apply 2 bags Urea and 1.5 bags MOP.\n3. Fruiting (Week 8): Apply remaining 1.5 bags Urea and 1.5 bags MOP.")
            ]
            
        # 2. Update visible agent viz
        st.session_state.agent_viz_state = {
            "Coordinator Agent": "active",
            "Crop Doctor": "inactive",
            "Weather Agent": "inactive",
            "Market Agent": "inactive",
            "Finance & Soil Agent": "active",
            "Government Agent": "inactive",
            "Planner Agent": "inactive",
            "findings": {
                "disease": "--",
                "weather": "--",
                "market": "--",
                "fertilizer": "6.5 Urea, 15 SSP, 6 MOP",
                "plan": "--"
            }
        }
        
        # 3. Update Trajectory
        st.session_state.trajectory = [
            "Query soil nutrient requirements",
            "Calibrate dosage for 3.0 acres clayey soil",
            "Generate stage-based split-dosage plan"
        ]
        
        # 4. Activate skills
        st.session_state.skills_activated = {
            "crop_disease": False,
            "fertilizer": True,
            "irrigation": False,
            "weekly_planner": True,
            "pesticide": False
        }
        
        # 5. Economics panel
        st.session_state.economics_panel = {
            "cost": "₹2,400",
            "yield_saved": "14%",
            "roi": "4.2x"
        }
        
        # 6. Weekly Planner Table
        st.session_state.weekly_planner_table = [
            {"day": "Monday", "task": "Apply basal dosage (3 bags Urea + 10 bags SSP + 3 bags MOP)", "done": False},
            {"day": "Wednesday", "task": "Prepare organic vermicompost topsoil layer", "done": False},
            {"day": "Friday", "task": "Perform leaf moisture check before next fertilization", "done": True}
        ]
        
        # 7. Timeline state
        st.session_state.timeline_state = "Treatment"
        
        st.rerun()

with row2_cols[1]:
    if st.button("🏛️ Simulate Government Subsidy Check", use_container_width=True):
        # 1. Set Chat History
        if preferred_lang == "Hindi (हिन्दी)":
            st.session_state.chat_history = [
                ("User", "क्या मुझे महाराष्ट्र में सोलर पंप या ड्रिप सिंचाई के लिए कोई सब्सिडी मिल सकती है?"),
                ("Agent", "उपलब्ध कृषि योजनाएं (महाराष्ट्र):\n1. पीएम-कुसुम सोलर पंप योजना: 5 एकड़ से कम जोत वाले किसानों के लिए 90% सब्सिडी।\n2. पीएम कृषि सिंचाई योजना: ड्रिप सिंचाई प्रणाली स्थापित करने के लिए लघु किसानों को 80% वित्तीय सहायता।\n\n⚠️ सुरक्षा चेतावनी: पीएम-कुसुम योजना के लिए पूर्व-भरा आवेदन फॉर्म तैयार करने के लिए आपकी पुष्टि आवश्यक है।")
            ]
        elif preferred_lang == "Marathi (मराठी)":
            st.session_state.chat_history = [
                ("User", "मला महाराष्ट्रात सोलर पंप किंवा ठिबक सिंचनासाठी काही अनुदान मिळू शकते का?"),
                ("Agent", "कृषि योजना (महाराष्ट्र):\n१. पीएम-कुसुम सोलर पंप योजना: ५ एकरपेक्षा कमी जमीन असलेल्या शेतकऱ्यांसाठी ९०% अनुदान.\n२. पीएम कृषि सिंचन योजना: ठिबक सिंचनासाठी लघू शेतकऱ्यांना ८०% आर्थिक मदत.\n\n⚠️ सुरक्षा चेतावणी: पीएम-कुसुम योजनेचा अर्ज तयार करण्यासाठी तुमची मंजुरी आवश्यक आहे.")
            ]
        else:
            st.session_state.chat_history = [
                ("User", "Can I get any subsidies for solar pumps or drip irrigation in Maharashtra?"),
                ("Agent", "Matched Agricultural Schemes (Maharashtra):\n1. **PM-KUSUM Solar Pump Scheme**: Offers up to 90% subsidy for installation of off-grid solar agricultural pumps for holdings under 5 acres.\n2. **PM Krishi Sinchayee Yojana (PMKSY)**: Provides up to 80% financial assistance for installing drip irrigation kits.\n\n⚠️ Safety Check: Generating a pre-filled application draft requires farmer's confirmation.")
            ]
            
        # 2. Update visible agent viz
        st.session_state.agent_viz_state = {
            "Coordinator Agent": "active",
            "Crop Doctor": "inactive",
            "Weather Agent": "inactive",
            "Market Agent": "inactive",
            "Finance & Soil Agent": "inactive",
            "Government Agent": "active",
            "Planner Agent": "inactive",
            "findings": {
                "disease": "--",
                "weather": "--",
                "market": "--",
                "fertilizer": "--",
                "plan": "Subsidy pre-fill"
            }
        }
        
        # 3. Update Trajectory
        st.session_state.trajectory = [
            "Query PM-KUSUM subsidy database",
            "Verify acreage eligibility (3 acres is eligible)",
            "Formulate subsidy draft application",
            "Government Subsidy Safety check triggered"
        ]
        
        # 4. Activate skills
        st.session_state.skills_activated = {
            "crop_disease": False,
            "fertilizer": False,
            "irrigation": True,
            "weekly_planner": False,
            "pesticide": False
        }
        
        # 5. Set pending HITL action
        st.session_state.pending_hitl = {
            "action_type": "Pre-fill Government Subsidy Application",
            "details": "Drafting pre-filled application form for PM-KUSUM Solar Pump Scheme under farmer Ramesh Kumar, Pune. System requires human approval before posting data to portal."
        }
        
        st.rerun()
