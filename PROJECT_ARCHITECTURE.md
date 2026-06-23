# 🩺 MediSecure-AI - Simple Project Architecture Guide

This guide explains how **MediSecure-AI** works in simple, easy-to-understand language. We avoid complex coding terms so that any student or teacher can follow along.

---

## 1. The Restaurant Analogy (How it all fits together)

Think of MediSecure-AI like a modern restaurant:

1. **The Customer's Table (The Page - `index.html`)**: This is the screen where the user enters details, uploads a medical report, runs calculations, and views their dynamic glassmorphic fitness cards and chat interface.
2. **The Waiter (The Director - [app.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/app.py))**: The waiter stands in the middle. When the customer submits a form or requests a Google Fit sync, the waiter coordinates requests with the different kitchen chefs and returns the final results.
3. **The Kitchen Chefs (The Logic Files - `/src/mlproject/`)**:
   * **Chef 1: The Mathematician ([prediction_pipeline.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/pipelines/prediction_pipeline.py))**: Takes age, BMI, location, and modifiers to calculate base premium.
   * **Chef 2: The PDF Reader ([medical_report_processor.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/medical_report_processor.py))**: Reads the uploaded medical report and flags chronic diseases.
   * **Chef 3: The Health Advisor ([health_risk_predictor.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/health_risk_predictor.py))**: Computes health scores, plans milestone checklists, and drafts adaptive activity workouts.
   * **Chef 4: The Chat Partner ([gemini_chatbot.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/gemini_chatbot.py))**: Converses with users about terms, सेक्शन 80D tax savings, and insurance comparisons.
   * **Chef 5: The Sync Specialist ([google_fit.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/google_fit.py))**: Initiates secure OAuth 2.0 sessions and fetches daily steps, sleep, hydration, and active time from Google Fitness REST API endpoints.
4. **The Store Room (The Storage)**:
   * **The Recipe Book (`model.pkl` & `preprocessor.pkl`)**: The mathematical rules taught to our Random Forest model from past insurance data.
   * **The Notebook (`chat_history.db`)**: An SQLite database file storing chat messages and active user profiles.

---

## 2. Step-by-Step Flow: What Happens During Sync & Live Underwrite?

When you press the button to sync your Google Fit metrics, the system executes 3 main actions:

1. **Calculate Actuarial Discounts (Actuarial Adjuster):**
   The backend retrieves the user's previously predicted base premium. Depending on the actual steps, sleep, water, and active time synced, the adjuster calculates a dynamic discount of up to **15%**. The base premium is reduced and returned to the UI alongside a health score boost (e.g. +8 points).
2. **Scan for Chronic Strain Risks (AI Clinical Warnings):**
   The system cross-references synced metrics against pre-existing conditions from the medical report. If the user has Hypertension and sleep is under 6 hours, it flags a *Cardiovascular Stress Alert*. Blinking warning cards render directly under the metrics grid.
3. **Draft Target-booster Workouts (Adaptive Workout Planner):**
   The planner reviews which daily goals are missing (e.g. steps or sleep) and generates a target-booster exercise routine (e.g., an Adrenal Sparing core sequence if sleep debt is found) to complete their daily targets safely.

---

## 3. Modularity Design Decisions (Answers for Teachers)

If a teacher asks **"Why is the code divided into so many files?"**, you can give these three simple reasons:

1. **Single Responsibility Principle (SRP)**:
   Each module has one focus. `google_fit.py` only handles OAuth connection and fetching; it knows nothing about pricing models or chat tables. If the Google Fit API changes, you only modify this file.
2. **Graceful UI Separation**:
   Adding premium cards (Adjuster, Alerts, Planner) doesn't clutter other tabs. The components reside within a single hidden container `#fit-sync-details` that only reveals itself when the sync completes.
3. **Persistent session context**:
   Using `get_user_profile(session_id)` from SQLite enables the `/google-fit/sync` route to look up user health calculations automatically without requiring the client to resend their profile data.