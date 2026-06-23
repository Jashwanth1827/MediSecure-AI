# MediSecure-AI - Health Insurance Premium Calculator

## Project Report

---

## 1. Project Overview

**Project Name:** MediSecure-AI  
**Project Type:** Machine Learning & Wearable Integration Web Application  
**Domain:** Real-Time Health Insurance Premium Prediction & Telematics Underwriting

### Objective
To develop an intelligent health insurance premium calculator that mirrors modern insurance practices, combining machine learning prediction, PDF medical report parsing, and real-time wearable telemetry (Google Fit) to implement dynamic, behavior-driven premium discounts, early-warning alerts, and adaptive fitness planners.

---

## 2. Real Insurance Factors Implemented

### 2.1 Premium Calculation Components

Our system calculates premiums using industry-standard base parameters:

| Factor | Options | Impact |
|--------|---------|--------|
| **Sum Insured** | 5L, 10L, 15L, 25L, 50L, 1Cr | Higher coverage = Higher premium |
| **Policy Term** | 1, 2, 3 Years | Multi-year = Discount |
| **Room Type** | General, Semi-Private, Private | Better room = Higher premium |
| **Deductible** | 0, 25K, 50K, 1L, 2L | Higher deductible = Lower premium |
| **Co-pay** | 0%, 10%, 15%, 20%, 25% | Higher co-pay = Lower premium |
| **NCB (No Claim Bonus)** | 0%, 20%, 25%, 33%, 45%, 50% | Claim-free years = Discount |
| **Add-on Riders** | None, Basic, Comprehensive, Premium | More riders = Higher premium |

### 2.2 Risk Loadings (Standard Insurance Practice)

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

### 2.3 Behavior-Driven Wearable Discounts (Telematics Underwriting)
Following the latest IRDAI guidelines in India allowing "Pay-As-You-Live" models, we implement a real-time **Actuarial Adjuster** reducing the base premium by up to **15%** for achieving daily health goals:

- **Steps (5% max):** Up to 5% discount for completing 10,000 steps.
- **Sleep (3% max):** Up to 3% discount for completing 8 hours of sleep.
- **Hydration (2% max):** Up to 2% discount for completing 3 liters of water.
- **Active Time (5% max):** Up to 5% discount for completing 30 minutes of physical activity.

---

## 3. Wearable Integration & Dynamic Modules

### 3.1 Google Fitness REST API Integration
- **Authorization Flow:** OAuth 2.0 Authorization Code Flow.
- **Endpoints Used:**
  - `https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate` (steps, hydration, active minutes)
  - `https://www.googleapis.com/fitness/v1/users/me/sessions` (sleep duration sessions)

### 3.2 Dynamic Actuarial Premium Adjuster
- Instantly reduces the user's base calculated premium.
- Displays Base Premium, Synced Discount %, Adjusted Annual Premium, and an active **Health Score Boost** (up to +10 points) on the frontend.

### 3.3 AI Clinical Early Warnings
Generates clinical alerts with blinking warning indicators when fitness targets are missed, cross-referencing chronic illnesses:
- **Cardiovascular Strain Alert:** Sleep < 6.0 hrs for users with Hypertension or Heart Disease.
- **Insulin Sensitivity Warning:** Active Time < 15 mins for users with Diabetes or Obesity.
- **Bronchial Spasm Strain Alert:** Active Time > 45 mins for users with Asthma or COPD.
- **Dehydration Warning:** Daily water intake < 1.2 Liters.

### 3.4 Adaptive AI Workout Planner
Drafts daily workouts dynamically:
- **Sleep Debt:** Prescribes adrenal-sparing stretching core recovery exercises.
- **Step Deficit:** Structures low-impact walking and shadow-boxing booster exercises.
- **Goals Achieved:** Prescribes recovery and progressive muscle relaxation stretches.

---

## 4. Technology Stack

- **Backend:** Python 3.10, Flask
- **ML Engine:** Scikit-learn (Random Forest Regressor)
- **API Orchestrator:** Google Fitness REST API (OAuth 2.0)
- **Database:** SQLite (persistent chat logs and user profiles)
- **GenAI:** Google Gemini API (`google-genai` SDK) + Local Fallback
- **Frontend:** HTML5, CSS3, JavaScript (Glassmorphism theme, dynamic SVG rings, pulse animation keyframes)

---

## 5. ML Model Performance

- **Algorithm:** Random Forest Regressor
- **Training R2:** 0.9460
- **Test R2:** 0.8632
- **Training MAE:** Rs. 1,524
- **Test MAE:** Rs. 2,616
- **Feature Importance:** Smoker (63.5%), BMI (17.4%), Age (12.1%), Dependents (1.0%), NCB (0.5%).

---

## 6. Premium Calculation Formula

```
Adjusted Annual Premium = 
    [ Base Predicted Premium 
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
      + Disease Cost ] 
    x (1 - Wearable Discount %)
```

---

## 7. Conclusion

MediSecure-AI calculations mirror modern **"telematics-driven"** insurance practices. It replaces static calculators with a dynamic ecosystem where users can lower their annual premium in real time by connecting wearable devices and maintaining healthy physical activity, sleep, and hydration parameters.
