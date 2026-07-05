# ruff: noqa
import os
import google.auth

# Load environment variables from .env file if it exists
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                k = key.strip()
                v = val.strip().strip('"').strip("'")
                os.environ[k] = v

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Import custom tools
from app.tools import (
    get_weather_forecast,
    diagnose_crop_disease,
    search_government_schemes,
    calculate_fertilizer_and_soil,
    search_market_prices,
    recommend_irrigation,
    schedule_calendar_reminder,
    save_to_drive,
    request_human_confirmation
)

# Setup GCP environment variables for local/cloud ADK execution
if "GOOGLE_CLOUD_PROJECT" not in os.environ:
    try:
        _, project_id = google.auth.default()
        if project_id:
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    except Exception:
        pass

if "GOOGLE_CLOUD_LOCATION" not in os.environ:
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

if "GOOGLE_GENAI_USE_VERTEXAI" not in os.environ:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

from functools import cached_property

class ConfiguredGemini(Gemini):
    @cached_property
    def api_client(self):
        from google.genai import Client
        vertexai = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True") == "True"
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        if vertexai:
            return Client(vertexai=True, project=project, location=location)
        else:
            return Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Configure the LLM model
llm_model = ConfiguredGemini(
    model="gemini-2.5-flash",
    retry_options=types.HttpRetryOptions(attempts=3),
)

# 1. Crop Doctor Agent (Vision & Diagnosis)
crop_doctor_agent = Agent(
    name="crop_doctor_agent",
    model=llm_model,
    instruction="""You are the Crop Doctor Agent.
    Your capability is to diagnose crop diseases, insect pests, and weed issues from visual descriptions or leaf images.
    If the user uploads/inputs an image (represented as base64), you MUST use the `diagnose_crop_disease` tool.
    Explain why the disease developed and offer two tiers of treatment:
    1. Organic/Biological (preferred).
    2. Chemical (include safety gear warnings: masks, gloves, proper dosage).
    Always warn the farmer to check the labels and consult local agricultural extension officers for critical issues.
    If you recommend a chemical pesticide, remind the farmer about safety and request confirmation before generating a full prescription by calling the `request_human_confirmation` tool.""",
    description="Specialist in identifying plant diseases, leaf spots, insect pests, weeds, and recommending biological and chemical treatments.",
    tools=[diagnose_crop_disease, request_human_confirmation],
)

# 2. Weather Agent (Forecasts & Irrigation)
weather_agent = Agent(
    name="weather_agent",
    model=llm_model,
    instruction="""You are the Weather Advisor Agent.
    Your capability is to retrieve weather forecasts and translate them into actionable farming advice.
    Use `get_weather_forecast` to check the forecast for the farmer's location.
    Suggest watering/irrigation adjustments using `recommend_irrigation` depending on growth stage and rain alerts.
    Warn the farmer of crop hazards like frost, high heat, and rain, advising on protections.""",
    description="Specialist in weather forecasting, weather alerts (rain, heat stress, frost), and rain-adjusted watering schedules.",
    tools=[get_weather_forecast, recommend_irrigation],
)

# 3. Market Agent (Mandi Prices & Trends)
market_agent = Agent(
    name="market_agent",
    model=llm_model,
    instruction="""You are the Market Agent.
    Your capability is to fetch wholesale Mandi prices for crops in nearby markets and recommend selling strategies.
    Use the `search_market_prices` tool.
    Analyze price trends, list the closest markets, suggest the best days to sell, and advise on post-harvest handling (like drying or cooling) to maximize profits.""",
    description="Specialist in wholesale market prices (Mandi), price trends, nearby selling spots, and optimal sell-timing strategies.",
    tools=[search_market_prices],
)

# 4. Finance & Soil Agent (Fertilizers & Cost Estimation)
finance_agent = Agent(
    name="finance_agent",
    model=llm_model,
    instruction="""You are the Finance and Soil Advisor Agent.
    Your capability is to calculate soil nutrient/fertilizer requirements, cost estimates, and fertilizer schedules.
    Use the `calculate_fertilizer_and_soil` tool.
    Provide exact split dosages of N-P-K (Nitrogen, Phosphorus, Potassium) in terms of urea, SSP, and MOP bags.
    Suggest organic alternatives (vermicompost, green manure) to improve long-term soil biology.""",
    description="Specialist in N-P-K fertilizer schedules, bag requirements, soil type adjustments, organic alternatives, and cost estimates.",
    tools=[calculate_fertilizer_and_soil],
)

# 5. Government Agent (Schemes & Subsidies)
government_agent = Agent(
    name="government_agent",
    model=llm_model,
    instruction="""You are the Government Schemes Advisor Agent.
    Your capability is to explain agricultural schemes, subsidies, eligibility, and required documents.
    Use the `search_government_schemes` tool.
    Check if the farmer is eligible for irrigation, solar pump, crop insurance, or organic subsidies, and walk them through required paperwork.
    Before generating a pre-filled subsidy application draft, tell the farmer what you will draft and let them know that their confirmation is required by calling the `request_human_confirmation` tool.""",
    description="Specialist in agricultural subsidies, government schemes, crop insurance, solar pumps, and eligibility requirements.",
    tools=[search_government_schemes, request_human_confirmation],
)

# 6. Report & Reminders Agent (Calendar & Drive MCP Sync)
report_agent = Agent(
    name="report_agent",
    model=llm_model,
    instruction="""You are the Report and Reminders Agent.
    Your capability is to save logs to Drive and schedule reminders in the Google Calendar.
    Use `save_to_drive` to archive plans and diagnosis history.
    Use `schedule_calendar_reminder` to schedule fertilizer applications, sprays, or follow-ups.
    Provide the farmer with confirmation of what was scheduled/saved.""",
    description="Specialist in scheduling follow-up calendar reminders and archiving crop plans and diagnoses in Google Drive.",
    tools=[save_to_drive, schedule_calendar_reminder],
)

# 7. Coordinator Agent (Parent Router)
root_agent = Agent(
    name="coordinator_agent",
    model=llm_model,
    instruction="""You are the FarmGuardian AI Coordinator.
    Your job is to assist smallholder farmers by routing their queries to the correct specialized sub-agents:
    - Transfer to `crop_doctor_agent` for leaf disease spots, pest, or weed diagnosis (including image analysis).
    - Transfer to `weather_agent` for weather forecast, rain alerts, or watering schedules.
    - Transfer to `market_agent` for mandi prices, market rates, or sell timing.
    - Transfer to `finance_agent` for fertilizer scheduling, NPK inputs, or soil health.
    - Transfer to `government_agent` for government subsidies, crop insurance, and schemes.
    - Transfer to `report_agent` for saving reports to Drive or scheduling reminders.
    
    Planning Capability:
    If a farmer has a multi-step query (e.g. "Identify tomato spots, check weather, recommend fertilizer, and find market prices"), you must create a brief plan:
    1. Transfer to Crop Doctor for diagnosis.
    2. Transfer to Weather Agent for conditions.
    3. Transfer to Finance Agent for soil/fertilizer plan.
    4. Transfer to Market Agent for mandi pricing.
    5. Transfer to Report Agent to save.
    Execute these steps by calling the appropriate transfers sequentially or routing the user turns.
    
    Security & Human-in-the-loop:
    Be cautious. Remind farmers of safety wear when chemical sprays are mentioned.
    
    Multilingual Capability:
    You can chat in the farmer's local language (e.g., Hindi, Telugu, Tamil, Marathi, Kannada, Spanish, English). Detect their input language and output your responses and the sub-agents' responses in that language. Use translation or write instructions in that language as requested.
    """,
    sub_agents=[
        crop_doctor_agent,
        weather_agent,
        market_agent,
        finance_agent,
        government_agent,
        report_agent
    ],
)

# Define the ADK App
app = App(
    root_agent=root_agent,
    name="app",
)
