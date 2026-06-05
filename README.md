# MediSecure-AI
https://medi-secure-ai.vercel.app/

**Intelligent Health Insurance Premium Prediction Platform | Indian Market**

MediSecure-AI is a full-stack machine learning application that predicts health insurance premiums for the Indian market with high accuracy (R²: 0.8632, MAE: ~₹2,616). It goes beyond simple prediction by providing explainability, interactive what-if scenario planning, health risk assessment, PDF medical report analysis, fraud detection, competitor comparison, and an AI-powered chatbot — all in a modern, responsive web interface.

---

## Table of Contents

- [Features Overview](#features-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage Guide](#usage-guide)
- [API Endpoints](#api-endpoints)
- [Model Details](#model-details)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features Overview

### 1. Premium Prediction Engine
- Random Forest regression model trained on Indian health insurance data
- Supports 32 Indian states with zone-based cost factors (Zone A/B/C)
- Actuarial modifiers: Sum Insured, Policy Term, Room Type, Deductible, Co-pay, NCB, Riders
- Real-time premium calculation with factor breakdown

### 2. AI Explainability (SHAP)
- Feature contribution analysis showing exactly why a premium is high or low
- Waterfall-style breakdown: Age +₹X, Smoking +₹Y, NCB -₹Z
- Side-by-side user comparison highlighting factor differences

### 3. What-If Simulator
- Interactive sliders to modify BMI, smoking status, deductible, and more
- Real-time premium delta display: "Change BMI 30→25 saves ₹2,800/year"
- Scenario comparison across multiple policy configurations

### 4. Health Risk Score (0–100)
- Separate scoring model assessing health risk independent of premium
- Risk classification: Excellent (90-100) → Critical (0-39)
- Illustrates cases where same premium corresponds to different risk profiles
- AI-powered health insights and prevention recommendations

### 5. PDF Medical Report Analysis
- Upload medical reports (PDF) for automatic disease detection
- Keyword-based extraction of conditions and severity levels
- Premium adjustment based on detected health conditions
- Lab findings parsing and report summarization

### 6. Competitor Comparison
- Side-by-side comparison of 10+ Indian insurers:
  - HDFC ERGO, ICICI Lombard, Star Health, Bajaj Allianz, Niva Bupa
  - Care Health, Reliance General, ManipalCigna, National Insurance, Oriental Insurance
- Real claim settlement ratios (CSR), network hospital counts, and plan features
- Best value and cheapest plan recommendations

### 7. Fraud / Anomaly Detection
- Input validation against statistical distributions (z-score > 3 flagged)
- Business rule checks (age 18-80, BMI 10-60)
- Suspicious pattern detection and warning generation

### 8. Region-Based Premium Variation
- 32 Indian states with healthcare cost indices
- Urban vs rural classification
- Pollution and healthcare access considerations per zone

### 9. AI Chatbot (Google Gemini)
- Gemini-powered conversational insurance assistant
- Answers queries about premiums, plans, claims, tax benefits, and more
- Automatic local fallback when API quota is exhausted
- Session-based chat history stored in SQLite

### 10. Personalized Recommendations
- Actionable lifestyle advice with quantified premium savings
- "Quit smoking → Save ₹8,000/year", "Reduce BMI to 25 → Save ₹2,800/year"
- Timeline-based recommendations (immediate, 3-month, 1-year)

---

## Architecture

```
User Input → Input Validation (Fraud Check) → Premium Prediction (ML Model)
                  │                                     │
                  ▼                                     ▼
             Fraud Alerts                        Explainability (SHAP)
                                                       │
                    What-If Simulator ←─────────────────┘
                        │
                        ▼
              Health Risk Score → Recommendations
                        │
                        ▼
             Region Analysis → Competitor Comparison
                        │
                        ▼
                 Final Report + Action Plan
```

**Data Flow:**
1. User enters demographic and policy details via the web form
2. Optional PDF medical report is processed for disease detection
3. ML model predicts base premium using 13 engineered features
4. Actuarial modifiers (zone, age loading, BMI, smoking, deductible, NCB, riders) are applied
5. Disease cost adjustments from medical report analysis are added
6. Health risk score is calculated independently
7. Personalized recommendations and competitor comparisons are generated
8. Results are displayed with full explainability breakdown

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10, Flask |
| **ML Model** | Scikit-learn (Random Forest Regressor) |
| **Explainability** | SHAP (planned/integration-ready) |
| **AI Chatbot** | Google Gemini API (`google-genai`) + Local Fallback |
| **PDF Processing** | PyPDF2 |
| **Database** | SQLite (chat history, user profiles) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Deployment** | Docker, Git, Render/Heroku/AWS-ready |

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

# (Optional) Set Gemini API key for chatbot
# Create .env file and add:
# GEMINI_API_KEY=your_key_here
```

### Run the Application

```bash
python app.py
```

Open **http://localhost:8080** in your browser.

### Docker Deployment (Optional)

```bash
docker build -t medisecure-ai .
docker run -p 8080:8080 medisecure-ai
```

---

## Usage Guide

### 1. Calculate Premium
1. Fill in personal details: Age, Gender, BMI, Dependents, Smoker status, State
2. Select coverage options: Sum Insured, Policy Term, Room Type
3. Configure cost-saving options: Deductible, Co-pay, NCB, Riders
4. (Optional) Upload a PDF medical report for disease-based adjustments
5. Click **Calculate Premium** to view the result with full breakdown

### 2. Use the What-If Simulator
- Modify any input parameter and recalculate instantly
- Side-by-side comparison shows premium impact of each change

### 3. Chat with AI Assistant
- Click the chat bubble (bottom-right) to open the chatbot
- Ask questions like:
  - "How is my premium calculated?"
  - "Compare HDFC vs ICICI"
  - "What is NCB and how does it work?"
  - "How can I reduce my premium?"
  - "What tax benefits are available?"

### 4. Testing Custom Gemini API Key
- Navigate to `http://localhost:8080/admin/gemini-key`
- Enter your Gemini API key and click Apply
- The key is persisted to `.env` and the chatbot will use it

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET, POST | Main page — premium calculator form and results |
| `/chat` | POST | Send message to AI chatbot |
| `/chat/history` | GET | Retrieve chat history for current session |
| `/chat/clear` | POST | Clear chat history |
| `/api/profile` | GET | Get user profile for current session |
| `/api/premium-calculator` | GET | JSON premium calculator (query params) |
| `/admin/gemini-key` | GET, POST | Set/test Gemini API key at runtime |
| `/admin/refresh` | POST | Gracefully restart the Werkzeug dev server |

---

## Model Details

### Training Data
- Enhanced dataset with 32 Indian states and 15+ features
- Covers age 18-75, both genders, all BMI ranges
- Includes actuarial factors: sum insured, policy term, room type, deductible, co-pay, NCB, riders

### Model Performance
- **Algorithm:** Random Forest Regressor
- **Test R²:** 0.8632
- **MAE:** ~₹2,616
- **Features used (13):** age, sex, bmi, children, smoker, state, sum_insured, policy_term, room_type, deductible, copay, ncb, riders

### Feature Engineering
- State → Zone classification (A/B/C) with cost multipliers
- Age loading based on Indian actuarial tables
- BMI risk categories (underweight, normal, overweight, obese)
- Disease detection from PDF reports with severity-based cost adjustment

---

## Project Structure

```
MediSecure-AI/
├── app.py                          # Flask application entry point & routes
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── Dockerfile                      # Docker configuration
├── .gitignore
├── .env                            # Environment variables (API keys)
│
├── artifacts/                      # Serialized ML models
│   ├── model.pkl                   # Trained Random Forest model
│   └── preprocessor.pkl            # ColumnTransformer preprocessor
│
├── notebook/
│   └── data/
│       └── Health_insurance.csv    # Training dataset
│
├── src/
│   └── mlproject/
│       ├── gemini_chatbot.py       # Gemini AI chatbot + local fallback + SQLite storage
│       ├── health_risk_predictor.py # Health risk scoring, prevention plans, AI insights
│       ├── insurance_company_data.py # 10 Indian insurers with plans, CSR, network data
│       ├── medical_report_processor.py # PDF extraction, disease detection, cost adjustment
│       │
│       └── pipelines/
│           └── prediction_pipeline.py # CustomData, PredictPipeline, premium modifiers
│
├── templates/                      # Jinja2 HTML templates
│   ├── index.html                  # Main application UI
│   └── gemini_key.html             # Gemini API key test page
│
├── static/                         # Static assets
├── logs/                           # Application logs
└── chat_history.db                 # SQLite database (auto-generated)
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate tests.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Contact

**Project Maintainer:** Jashwanth  
**GitHub:** [Jashwanth1827](https://github.com/Jashwanth1827)  
**Project Link:** [https://github.com/Jashwanth1827/MediSecure-AI](https://github.com/Jashwanth1827/MediSecure-AI)

---

*MediSecure-AI — Making health insurance transparent, understandable, and accessible for everyone in India.*
