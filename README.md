# MediSecure-AI
https://medi-secure-ai.vercel.app/

**Intelligent Health Insurance Premium Prediction Platform with Google Fit Real-Time Underwriting**

MediSecure-AI is a full-stack machine learning application that predicts health insurance premiums for the Indian market with high accuracy (R²: 0.8632, MAE: ~₹2,616). The platform extends standard static predictions by introducing real-time health-wearable integration using the **Google Fitness REST API**, dynamic actuarial premium adjustments, AI clinical alerts, an adaptive workout planner, PDF medical report parsing, fraud anomaly detection, and a SQLite-backed conversational insurance advisor powered by Google Gemini.

---

## Table of Contents

- [Features Overview](#features-overview)
- [Wearable Real-Time Underwriting Pipeline](#wearable-real-time-underwriting-pipeline)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage Guide](#usage-guide)
- [API Endpoints](#api-endpoints)
- [Model Details](#model-details)
- [Project Structure](#project-structure)
- [License](#license)
- [Contact](#contact)

---

## Features Overview

### 1. Premium Prediction Engine
- Random Forest regression model trained on Indian health insurance data.
- Supports 32 Indian states with zone-based cost factors (Zone A/B/C).
- Actuarial modifiers: Sum Insured, Policy Term, Room Type, Deductible, Co-pay, NCB, Riders.
- Real-time premium calculation with factor breakdown.

### 2. Google Fit OAuth 2.0 Integration & Synced Metrics
- Connects securely to the Google Fitness REST API.
- Retrieves daily actual steps, sleep hours, water intake, and active minutes.
- Redesigned premium dark-mode dashboard displaying metrics in a responsive grid of glassmorphic cards with animated SVG progress rings.

### 3. Dynamic Actuarial Premium Adjuster
- Dynamically discounts calculated insurance premiums in real time (up to **15% savings**) as the user meets physical fitness targets.
- Displays base calculated premium, discount breakdown, adjusted annual cost, and health score boosts.

### 4. AI Early Warning Clinical Alerts
- Cross-references daily synced fitness data against chronic conditions extracted from the user's medical profile (e.g. Hypertension, Diabetes, Asthma).
- Triggers visual alert cards with pulse animations warning of cardiac strain, insulin sensitivity drops, or dehydration risks.

### 5. Adaptive AI Workout Planner
- Re-writes and structures the prescriptive workout program dynamically depending on daily activity deficits or sleep debt (e.g. Adrenal-sparing core stretches for sleep deprivation, stepping cardio for low step counts).

### 6. PDF Medical Report Analysis
- Upload medical reports (PDF) for automatic disease detection using keyword-based NLP.
- Extracted conditions and severity levels generate premium surcharges (+15% to +80%).
- Regular expression parsing of blood metrics (Glucose, HbA1c, Blood Pressure, Creatinine).

### 7. Competitor Comparison
- Side-by-side comparison of 10+ Indian insurers (HDFC ERGO, ICICI Lombard, Star Health, Bajaj Allianz, Niva Bupa, Care Health, Reliance General, ManipalCigna, National Insurance, Oriental Insurance).
- Real claim settlement ratios (CSR), network hospital counts, and plan features.

### 8. Fraud / Anomaly Detection
- Input validation against statistical distributions (z-score > 3 flagged).
- Business rule checks (age 18-80, BMI 10-60) and suspicious pattern checks.

### 9. AI Chatbot (Google Gemini)
- Gemini-powered conversational insurance assistant answering questions on tax benefits under Section 80D, riders, claims, and calculations.
- Automatic local rule-based fallback and session persistence stored in SQLite.

---

## Wearable Real-Time Underwriting Pipeline

```
[Google Fit REST API] ──► Synced Metrics ──► [Actuarial Adjuster] ──► Real-Time Discounted Premium
                                  │
                                  ├────────► [Clinical Alerts]    ──► Chronic Disease Strain Warnings
                                  │
                                  └────────► [Adaptive Planner]   ──► Deficit-Sparing Active Routines
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10, Flask |
| **ML Model** | Scikit-learn (Random Forest Regressor) |
| **Wearable API** | Google Fitness REST API (OAuth 2.0 Authorization Code Flow) |
| **AI/GenAI** | Google Gemini API (`google-genai`) + Local Fallback |
| **PDF Processing** | PyPDF2 |
| **Database** | SQLite (chat history, persistent session user profiles) |
| **Frontend** | HTML5, CSS3 (Vanilla Glassmorphic styling), SVG Animations, Vanilla JS |
| **Deployment** | Docker, Git, Render/Heroku-ready |

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/Jashwanth1827/MediSecure-AI.git
cd MediSecure-AI

# Install dependencies
pip install -r requirements.txt

# (Optional) Set Gemini API key for Chatbot
# Create a .env file and add:
# GEMINI_API_KEY=your_gemini_api_key_here
```

### Run the Application

```bash
python app.py
```

Open **http://localhost:8080** in your browser.

---

## Usage Guide

1. **Calculate Baseline Premium:**
   Fill in personal details (Age, Gender, BMI, Dependents, State, Smoking) and configure policy parameters (Sum Insured, Deductibles, Co-pays). Optionally upload a PDF medical report. Click **Calculate Premium**.

2. **Connect Wearables:**
   Navigate to the **Google Fit** tab and click **Connect Account** to authorize Google Fit API access.

3. **Sync & Live-Underwrite:**
   Click **Sync Now** inside the Google Fit Integration panel. Your steps, sleep, hydration, and active minutes will be pulled in. The dashboard will instantly animate SVG rings and calculate:
   - Your premium discount under the **Actuarial Premium Adjuster**.
   - Custom **Clinical Strain Warnings** if you have chronic illnesses and low fitness parameters.
   - An **Adaptive Workout Routine** targeting your fitness deficits.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET, POST | Main page — premium calculator form and results |
| `/chat` | POST | Send message to AI chatbot |
| `/chat/history` | GET | Retrieve chat history for current session |
| `/chat/clear` | POST | Clear chat history |
| `/google-fit/connect` | GET | Initiates OAuth 2.0 authorization code flow with Google Fit |
| `/google-fit/callback` | GET | Handles authorization code exchange for tokens |
| `/google-fit/sync` | GET | Fetches Google Fit metrics, adjusts premium, and compiles alerts/workouts |
| `/google-fit/disconnect` | POST | Clears Google Fit credentials and tokens from user session |
| `/admin/gemini-key` | GET, POST | Set/test Gemini API key at runtime |

---

## Model Details

- **Algorithm:** Random Forest Regressor
- **Test R²:** 0.8632
- **MAE:** ~₹2,616
- **Features used (13):** age, sex, bmi, children, smoker, state, sum_insured, policy_term, room_type, deductible, copay, ncb, riders.
- **Actuarial Adjustments:** Zone A/B/C modifiers (1.15x metro, 1.0x tier 1, 0.88x tier 2), smoking surcharge (+40%), age loading (+8% to +25%), BMI loading (+5% to +20%), disease loading (+15% to +80%).

---

## Project Structure

```
MediSecure-AI/
├── app.py                          # Flask application entry point & routes
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── Dockerfile                      # Docker configuration
├── .env                            # Environment variables (API keys)
│
├── artifacts/                      # Serialized ML models
│   ├── model.pkl                   # Trained Random Forest model
│   └── preprocessor.pkl            # ColumnTransformer preprocessor
│
├── notebook/data/
│   └── Health_insurance.csv    # Training dataset
│
├── src/mlproject/
│   ├── google_fit.py               # Google Fitness REST API communication logic
│   ├── gemini_chatbot.py           # Gemini AI chatbot & SQLite database connection
│   ├── health_risk_predictor.py    # Health scoring, prevention plans, adaptive workouts
│   ├── insurance_company_data.py   # 10 Indian insurers CSR and plan features
│   ├── medical_report_processor.py # PDF report extraction & regex laboratory parsing
│   └── pipelines/
│       └── prediction_pipeline.py  # CustomData DTO, PredictPipeline, modifiers
│
├── templates/                      # Jinja2 HTML templates
│   ├── index.html                  # Main application UI
│   └── gemini_key.html             # Gemini API key test page
│
├── chat_history.db                 # SQLite database (auto-generated)
└── logs/                           # Event logs
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Contact

**Project Maintainer:** Jashwanth  
**GitHub:** [Jashwanth1827](https://github.com/Jashwanth1827)  
**Project Link:** [https://github.com/Jashwanth1827/MediSecure-AI](https://github.com/Jashwanth1827/MediSecure-AI)
