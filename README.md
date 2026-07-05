# FarmGuardian AI - Smart Farming Companion

**FarmGuardian AI** is an intelligent agricultural assistant designed to help smallholder farmers manage crop diseases, weather changes, fertilizer usage, and government subsidies. Rather than a single chatbot, it implements a **Multi-Agent Orchestration** system where specialized agents handle different agricultural domains.

---

## 🏗️ Multi-Agent Architecture

```
                    Farmer
                       │
             Coordinator Agent (Router/Planner)
                       │
 ┌──────────┬──────────┬──────────┬──────────┐
 │          │          │          │          │
Crop     Weather    Market    Finance   Government
Doctor    Agent      Agent      Agent      Agent
 │
Soil Advisor
 │
Planning Agent
 │
Report Agent
```

1. **Coordinator Agent**: Routes incoming queries to specialized sub-agents, manages language preferences, and orchestrates multi-step agricultural plans.
2. **Crop Doctor Agent**: Performs multimodal crop disease, pest, and weed diagnosis from uploaded images using Gemini Vision.
3. **Weather Agent**: Retrieves regional weather forecasts and issues warnings for frost, rain, or heat stress.
4. **Market Agent**: Monitors wholesale market prices (Mandi rates) and suggests optimal days/locations to sell.
5. **Finance Agent**: Recommends fertilizer scheduling (exact Urea, SSP, MOP bags per acre) and soil health improvements.
6. **Government Agent**: Identifies subsidies, schemes, and insurance programs for which the farmer is eligible.
7. **Report Agent**: Mock integrations for archiving diagnostic reports to Google Drive and scheduling crop care reminders in Google Calendar (MCP concept).

---

## 📚 Agent Skills Directory (`skills/`)

The application features progressive disclosure of capabilities via separate Agent Skills:
* `crop_disease/`: Crop disease pathology, pests, weed identification, and bio/chemical treatment plans.
* `weather_planning/`: Temperature, wind, humidity interpretation and operation alerts.
* `fertilizer_advisor/`: Crop N-P-K nutrient split-scheduling and soil-type calibrations.
* `government_scheme/`: PM-KISAN, crop insurance, solar pump, and horticulture subsidies.
* `market_prices/`: Mandi wholesale pricing database and selling strategies.
* `irrigation/`: Watering requirement logic adjusted for rainfall projections.
* `harvest_planning/`: Maturity indexing and post-harvest handling advice.

---

## 🚀 How to Run the App

1. **Install Dependencies**:
   Ensure `uv` is installed, then sync the dependencies:
   ```bash
   uv sync
   ```

2. **Launch Streamlit Dashboard**:
   Run the dashboard app:
   ```bash
   uv run streamlit run app/streamlit_app.py
   ```

3. **Explore Demo Scenarios**:
   Click on the quick triggers at the bottom of the page to immediately run typical flows (Disease Diagnosis, Weather & Watering, or Mandi Prices).

---

## 🛡️ Security & Evaluation

* **Human-in-the-Loop (HITL)**: Before generating chemical spray reminders or drafting subsidy forms, the system flags the action and requires explicit farmer confirmation in the UI to prevent dangerous pesticide usage or incorrect form submissions.
* **Agricultural Guardrails**: Validates N-P-K fertilizer rates to prevent soil over-nitrification and chemical runoffs.
* **Evaluation Dataset**: A curated set of farming scenarios is available at `tests/eval/datasets/farming-scenarios.json` to evaluate agent performance across domains using `agents-cli eval`.
