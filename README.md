# FarmGuardian AI - Smart Farming Companion

**FarmGuardian AI** is an intelligent agricultural assistant designed to help smallholder farmers manage crop diseases, weather changes, fertilizer usage, and government subsidies. Rather than a single chatbot, it implements a **Multi-Agent Orchestration** system where specialized agents handle different agricultural domains.

---

## 🏗️ Multi-Agent Architecture

```
                                Farmer
                                  │
                       ┌──────────────────────┐
                       │  Coordinator Agent   │
                       └──────────┬───────────┘
                                  │
        ┌──────────────┬──────────┼──────────┬──────────────┬──────────────┐
        │              │          │          │              │              │
  ┌───────────┐  ┌───────────┐┌───────────┐┌───────────┐  ┌───────────┐  ┌───────────┐
  │   Crop    │  │  Weather  ││  Market   ││ Finance & │  │Government │  │ Report &  │
  │  Doctor   │  │   Agent   ││   Agent   ││Soil Agent │  │   Agent   │  │ Reminders │
  └───────────┘  └───────────┘└───────────┘└───────────┘  └───────────┘  └───────────┘
```

1. **Coordinator Agent**: Parent router and planner. Detects query intent, manages language settings, and orchestrates multi-step agricultural plans across sub-agents.
2. **Crop Doctor Agent**: Diagnoses crop diseases, pests, and weed issues from uploaded leaf images using Gemini Vision.
3. **Weather Agent**: Retrieves regional weather forecasts and generates rain-adjusted watering recommendations.
4. **Market Agent**: Monitors wholesale market prices (Mandi rates) and recommends selling strategies.
5. **Finance & Soil Agent**: Recommends N-P-K fertilizer schedules based on soil type and land acreage.
6. **Government Agent**: Identifies regional subsidies (e.g. drip irrigation, solar pumps) and insurance programs.
7. **Report & Reminders Agent**: Handles productivity tasks like saving crop plans to Google Drive and scheduling follow-up fertilizer reminders in Google Calendar.

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
