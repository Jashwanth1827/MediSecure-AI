# MediSecure - Health Insurance Premium Calculator

## Project Report

---

## 1. Project Overview

**Project Name:** MediSecure  
**Project Type:** Machine Learning Web Application  
**Domain:** Real-Time Health Insurance Premium Calculation

### Objective
To develop an intelligent health insurance premium calculator that mirrors real insurance company practices, including medical report analysis, disease detection, and personalized premium calculations based on industry-standard factors.

---

## 2. Real Insurance Factors Implemented

### 2.1 Premium Calculation Components

Our system now calculates premiums using **real insurance industry factors**:

| Factor | Options | Impact |
|--------|---------|--------|
| **Sum Insured** | 5L, 10L, 15L, 25L, 50L, 1Cr | Higher coverage = Higher premium |
| **Policy Term** | 1, 2, 3 Years | Multi-year = Discount |
| **Room Type** | General, Semi-Private, Private | Better room = Higher premium |
| **Deductible** | 0, 25K, 50K, 1L, 2L | Higher deductible = Lower premium |
| **Co-pay** | 0%, 10%, 15%, 20%, 25% | Higher co-pay = Lower premium |
| **NCB (No Claim Bonus)** | 0%, 20%, 25%, 33%, 45%, 50% | Claim-free years = Discount |
| **Add-on Riders** | None, Basic, Comprehensive, Premium | More riders = Higher premium |

### 2.2 Risk Loadings (Real Insurance Practice)

| Risk Factor | Condition | Loading |
|-------------|-----------|---------|
| **Age** | 35+ years | +8% |
| **Age** | 40+ years | +15% |
| **Age** | 50+ years | +25% |
| **BMI** | 27-30 | +5% |
| **BMI** | 30-35 | +12% |
| **BMI** | 35+ | +20% |
| **Smoker** | Yes | +40% |
| **Disease (Mild)** | 1 condition | +15% |
| **Disease (Moderate)** | Multiple | +35% |
| **Disease (Severe)** | Critical | +80% |

### 2.3 Zone Classification (Real Indian Insurance)

Insurance companies classify cities into zones for pricing:

| Zone | Cities | Factor |
|------|--------|--------|
| **A (Metro)** | Delhi, Mumbai, Bangalore, Chennai, Hyderabad, Kolkata | 1.15x |
| **B (Tier 1)** | Pune, Ahmedabad, Surat, Chandigarh, Lucknow | 1.00x |
| **C (Tier 2/3)** | Other cities, Rural areas | 0.88x |

### 2.4 Deductible & Co-pay Savings

**Deductible** (Amount you pay before insurance kicks in):
- No Deductible: 1.00x
- Rs. 25,000: 0.85x (15% savings)
- Rs. 50,000: 0.75x (25% savings)
- Rs. 1,00,000: 0.65x (35% savings)
- Rs. 2,00,000: 0.55x (45% savings)

**Co-pay** (Percentage you pay on claim):
- 0%: 1.00x
- 10%: 0.92x
- 15%: 0.88x
- 20%: 0.85x
- 25%: 0.82x

### 2.5 No Claim Bonus (NCB)

Claim-free years earn discounts:
- 0 years: 1.00x (base)
- 1 year: 0.95x (5% discount)
- 2 years: 0.93x (7% discount)
- 3 years: 0.90x (10% discount)
- 4 years: 0.85x (15% discount)
- 5+ years: 0.80x (20% discount)

---

## 3. Medical Report Analysis

### 3.1 PDF Upload & Text Extraction
- Upload medical reports in PDF format
- Extract text using PyPDF2
- Analyze for disease indicators

### 3.2 Disease Detection
Detects 16+ conditions:
- Diabetes, Hypertension, Heart Disease, Cancer
- Kidney Disease, Liver Disease, Asthma, COPD
- Arthritis, Thyroid, Anemia, Pneumonia
- Tuberculosis, Mental Health, Depression, Anxiety

### 3.3 Severity Assessment
| Severity | Loading | Description |
|----------|---------|-------------|
| **Mild** | +15% | Early stage, controlled |
| **Moderate** | +35% | Requires monitoring |
| **Severe** | +80% | Critical, needs treatment |

---

## 4. Technology Stack

### Backend
- Python 3.10, Flask, Scikit-learn
- Pandas, NumPy, PyPDF2
- SQLite (chat history)

### Frontend  
- HTML5, CSS3, JavaScript
- Responsive design

### AI/ML
- Google Gemini AI (chatbot)
- Random Forest Regressor

---

## 5. ML Model Performance

| Metric | Value |
|--------|-------|
| **Algorithm** | Random Forest |
| **Training R2** | 0.9460 |
| **Test R2** | 0.8632 |
| **Training MAE** | Rs. 1,524 |
| **Test MAE** | Rs. 2,616 |

### Feature Importances
1. Smoker: 63.5%
2. BMI: 17.4%
3. Age: 12.1%
4. Children: 1.0%
5. NCB: 0.5%

---

## 6. Premium Calculation Formula

```
Annual Premium = 
    Base Premium
    x Sum Insured Factor
    x Zone Factor
    x Age Loading
    x BMI Loading  
    x Smoker Loading
    x Disease Loading
    x Deductible Factor
    x Co-pay Factor
    x NCB Factor
    + Rider Cost
    + Disease Cost
```

---

## 7. Project Structure

```
Health-Insurance-Prediction/
├── app.py                          # Flask application
├── requirements.txt                # Dependencies
├── .env                           # API keys
├── artifacts/
│   ├── model.pkl                  # Trained RF model
│   └── preprocessor.pkl           # Data transformer
├── notebook/data/
│   └── Health_insurance.csv       # Enhanced dataset
├── src/mlproject/
│   ├── medical_report_processor.py # PDF & disease analysis
│   ├── gemini_chatbot.py          # AI chatbot
│   └── pipelines/
│       └── prediction_pipeline.py  # Premium calculator
└── templates/
    └── index.html                # UI
```

---

## 8. How It Mirrors Real Insurance

| Aspect | Real Insurance | Our System |
|--------|---------------|------------|
| Age Loading | Yes | Yes |
| BMI Loading | Yes | Yes |
| Smoker Loading | Yes | Yes |
| Zone Classification | Yes | Yes |
| Sum Insured Tiers | Yes | Yes |
| Policy Term Discount | Yes | Yes |
| Deductible Savings | Yes | Yes |
| Co-pay Discount | Yes | Yes |
| NCB Discount | Yes | Yes |
| Rider Costs | Yes | Yes |
| Disease Loading | Yes | Yes |
| Medical Underwriting | Full | PDF-based |

---

## 9. Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (optional)
# Add to .env: GEMINI_API_KEY=your_key

# Run application
python app.py
```

Open: http://localhost:8080

---

## 10. Future Enhancements

1. **Image-based Medical Analysis** (X-rays, MRIs)
2. **Real-time Insurance API Integration**
3. **Multi-language Support**
4. **User Authentication**
5. **Policy Comparison Engine**

---

## 11. Conclusion

MediSecure now calculates insurance premiums using **real industry practices**:
- All major premium factors
- Zone-based pricing
- Risk loadings
- Cost-saving options
- Medical report analysis
- AI chatbot assistance

The system provides **accurate, personalized premium estimates** that closely mirror real insurance company calculations.

---

**Last Updated:** March 2026
