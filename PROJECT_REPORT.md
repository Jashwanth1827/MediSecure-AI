# 🏥 MediSecure - Health Insurance Prediction System

## Project Report

---

## 1. Project Overview

**Project Name:** MediSecure  
**Project Type:** Machine Learning Web Application  
**Domain:** Health Insurance Cost Prediction & AI Chat Assistant

### Objective
To develop an intelligent health insurance cost prediction system that analyzes medical reports, detects diseases, and provides personalized insurance recommendations through an AI-powered chatbot.

---

## 2. Problem Statement

Traditional health insurance estimation systems:
- Use outdated region-based pricing (US regions)
- Do not account for Indian state-wise healthcare costs
- Lack medical report analysis capabilities
- No AI-powered assistance for user queries

---

## 3. Features Implemented

### 3.1 Health Insurance Cost Prediction
| Feature | Description |
|---------|-------------|
| Age | User's age (1-120 years) |
| Gender | Male/Female |
| BMI | Body Mass Index (10-60) |
| Dependents | Number of dependents (0-15) |
| Smoker | Yes/No |
| State | Indian state (32 states) |

### 3.2 Medical Report Analysis
- **PDF Upload**: Upload medical reports in PDF format
- **Disease Detection**: Automatically detects 16+ diseases
- **Severity Assessment**: Categorizes as Mild/Moderate/Severe
- **Cost Adjustment**: Adds disease-based costs to prediction

**Detectable Diseases:**
- Diabetes, Hypertension, Heart Disease, Cancer
- Kidney Disease, Liver Disease, Asthma, COPD
- Arthritis, Thyroid, Anemia, Pneumonia, Tuberculosis
- Mental Health, Depression, Anxiety, Stroke, Dengue, Malaria

### 3.3 Indian State Healthcare Index
Real healthcare cost factors for 32 Indian states:

| State | Cost Factor | State | Cost Factor |
|-------|-------------|-------|-------------|
| Delhi | 1.85 | Madhya Pradesh | 1.20 |
| Maharashtra | 1.75 | Odisha | 1.25 |
| Karnataka | 1.65 | Rajasthan | 1.35 |
| Tamil Nadu | 1.55 | Gujarat | 1.45 |
| Kerala | 1.60 | Punjab | 1.40 |

### 3.4 AI Chatbot (MediBot)
- **Powered by Google Gemini AI**
- **Local Fallback Mode** (works without API)
- **Insurance Recommendations** based on user profile
- **Health Information** on diseases, claims, taxes
- **Quick Action Buttons** for common queries

**Chatbot Capabilities:**
- Insurance plan recommendations
- Claim process guidance
- Waiting period explanations
- Tax benefit information (Section 80D)
- Maternity coverage details
- Mental health coverage info
- Network hospital information

---

## 4. Technology Stack

### 4.1 Backend
| Technology | Purpose |
|------------|---------|
| Python 3.10 | Programming Language |
| Flask | Web Framework |
| Scikit-learn | Machine Learning |
| Pandas | Data Processing |
| NumPy | Numerical Computing |
| PyPDF2 | PDF Text Extraction |

### 4.2 AI/ML
| Technology | Purpose |
|------------|---------|
| Google Gemini AI | AI Chatbot (Gemini 2.0 Flash) |
| SQLite | Chat History & Profile Storage |
| Random Forest | Prediction Model |

### 4.3 Frontend
| Technology | Purpose |
|------------|---------|
| HTML5 | Page Structure |
| CSS3 | Styling & Animations |
| JavaScript | Interactive Chat Interface |

### 4.4 Additional Libraries
```
pandas, numpy, matplotlib, scikit-learn, flask
PyPDF2, Werkzeug, requests, google-genai, python-dotenv
```

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │ Prediction Form │  │ Medical Report  │  │ Chatbot    │ │
│  │                 │  │ Upload (PDF)    │  │ 💬         │ │
│  └────────┬────────┘  └────────┬────────┘  └─────┬──────┘ │
└───────────┼───────────────────┼──────────────────┼─────────┘
            │                   │                  │
            ▼                   ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │ Prediction      │  │ Medical Report   │  │ Gemini     │ │
│  │ Pipeline        │  │ Processor        │  │ Chatbot    │ │
│  └────────┬────────┘  └────────┬────────┘  └─────┬──────┘ │
└───────────┼───────────────────┼──────────────────┼─────────┘
            │                   │                  │
            ▼                   ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA & ML MODELS                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Model.pkl    │  │ Preprocessor │  │ Chat History DB  │ │
│  │ (Random      │  │ .pkl         │  │ (SQLite)        │ │
│  │ Forest)      │  │              │  │                  │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Machine Learning Model

### 6.1 Dataset
- **Original Dataset:** 1,338 records
- **Features:** 6 (age, sex, bmi, children, smoker, state)
- **Target:** charges (insurance cost in $)

### 6.2 Preprocessing
- **Numerical Features:** StandardScaler
- **Categorical Features:** OneHotEncoder (sex, smoker, state)

### 6.3 Model Selection
| Model | Training R² | Test R² |
|-------|-------------|---------|
| Random Forest | 0.9753 | 0.8571 |
| Linear Regression | 0.7394 | 0.7853 |
| Decision Tree | 0.9983 | 0.7348 |
| AdaBoost | 0.8304 | 0.8321 |

**Selected Model:** Random Forest Regressor
- Best balance of training and test accuracy
- Handles non-linear relationships well
- Robust to outliers

### 6.4 Cost Formula
```
Final Cost = (Base Prediction × State Factor) + Disease Cost
```

---

## 7. Project Structure

```
Health-Insurance-Prediction/
├── app.py                          # Flask application
├── requirements.txt                # Dependencies
├── .env                           # Environment variables
├── chat_history.db                # SQLite database
├── artifacts/
│   ├── model.pkl                  # Trained ML model
│   ├── preprocessor.pkl           # Data preprocessor
│   ├── train.csv                 # Training data
│   └── test.csv                  # Test data
├── notebook/
│   ├── data/
│   │   └── Health_insurance.csv  # Dataset
│   ├── 1_EDA.ipynb               # Exploratory Analysis
│   └── 2_MODEL_TRAINING.ipynb    # Model Training
├── src/mlproject/
│   ├── __init__.py
│   ├── logger.py
│   ├── exception.py
│   ├── utils.py
│   ├── medical_report_processor.py  # PDF & Disease Detection
│   ├── gemini_chatbot.py            # AI Chatbot
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   └── model_trainer.py
│   └── pipelines/
│       ├── training_pipeline.py
│       └── prediction_pipeline.py
└── templates/
    └── index.html                # Frontend UI
```

---

## 8. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET/POST | Main prediction page |
| `/chat` | POST | Send message to chatbot |
| `/chat/history` | GET | Get chat history |
| `/chat/clear` | POST | Clear chat history |
| `/api/profile` | GET | Get user profile |

---

## 9. Installation & Setup

### 9.1 Prerequisites
```bash
Python 3.8+
pip
```

### 9.2 Installation
```bash
# Clone repository
git clone https://github.com/mayurd8862/Health-Insurance-Prediction.git
cd Health-Insurance-Prediction

# Install dependencies
pip install -r requirements.txt

# Set API key (optional - for AI chatbot)
# Add to .env file:
# GEMINI_API_KEY=your_api_key

# Run application
python app.py
```

### 9.3 Access
Open browser: `http://localhost:8080`

---

## 10. Future Enhancements

1. **Image-based Medical Report Analysis**
   - OCR for handwritten reports
   - CNN for X-ray/MRI analysis

2. **RAG (Retrieval Augmented Generation)**
   - Medical knowledge base
   - Context-aware responses

3. **Real-time Data Updates**
   - Live healthcare cost data
   - Insurance plan database

4. **User Authentication**
   - Multi-user support
   - Profile persistence

5. **Insurance Provider Integration**
   - Real-time premium quotes
   - Policy comparison

---

## 11. Conclusion

MediSecure successfully combines:
- ✅ ML-based cost prediction
- ✅ Medical report analysis
- ✅ Indian state-wise pricing
- ✅ AI-powered chatbot assistance

The system provides accurate, personalized health insurance recommendations with comprehensive support through an intuitive web interface.

---

## 12. References

1. Scikit-learn Documentation: https://scikit-learn.org/
2. Flask Documentation: https://flask.palletsprojects.com/
3. Google Gemini API: https://ai.google.dev/
4. PyPDF2 Documentation: https://pypdf2.readthedocs.io/
5. Indian Healthcare Statistics: https://www.worldbank.org/

---

**Project Contributors:**  
**License:** MIT  
**Last Updated:** March 2026
