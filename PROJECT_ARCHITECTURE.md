# 🩺 MediSecure - Simple Project Architecture Guide

This guide explains how **MediSecure** works in simple, easy-to-understand language. We avoid complex coding terms so that any student or teacher can follow along.

---

## 1. The Restaurant Analogy (How it all fits together)

Think of MediSecure like a modern restaurant:

1. **The Customer's Table (The Page - `index.html`)**: This is the screen where the user enters their age, weight (BMI), location, and uploads a medical report. It is also where they see their final price and chat with the AI helper.
2. **The Waiter (The Director - [app.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/app.py))**: The waiter stands in the middle. When the customer submits the form, the waiter takes the info, runs to the kitchen to get the food prepared by different chefs, and brings the final results back to the table.
3. **The Kitchen Chefs (The Logic Files - `/src/mlproject/`)**:
   * **Chef 1: The Mathematician ([prediction_pipeline.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/pipelines/prediction_pipeline.py))**: Takes the user's age, BMI, and habits to calculate the basic insurance price.
   * **Chef 2: The PDF Reader ([medical_report_processor.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/medical_report_processor.py))**: Reads the uploaded medical report and flags diseases (like diabetes or heart issues).
   * **Chef 3: The Health Advisor ([health_risk_predictor.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/health_risk_predictor.py))**: Gives the user a health score out of 100 and tells them how to improve.
   * **Chef 4: The Chat Partner ([gemini_chatbot.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/gemini_chatbot.py))**: Talkative AI assistant that answers any questions about insurance policies.
4. **The Store Room (The Storage)**:
   * **The Recipe Book (`model.pkl` & `preprocessor.pkl`)**: The mathematical rules taught to our system from past data.
   * **The Notebook (`chat_history.db`)**: A database file that remembers what the user talked about so the AI chatbot doesn't forget.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Customer Table (index.html)                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                            1. Submits Profile
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         The Waiter (app.py)                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             ▼                      ▼                      ▼
┌────────────────────────┐  ┌────────────────┐  ┌──────────────────────┐
│     Chef 1 (Math)      │  │  Chef 2 (PDF)  │  │ Chef 3 (Advisor)     │
│ prediction_pipeline.py │  │  medical_...   │  │ health_predictor.py  │
└────────────────────────┘  └────────────────┘  └──────────────────────┘
```

---

## 2. Step-by-Step Flow: What Happens When You Click Predict?

When you press the button to calculate your insurance premium, the system executes 4 simple steps:

1. **Step 1: Read the PDF (PDF Reader)**
   If you uploaded a medical report, the PDF reader scanning tool goes through the document text. It looks for disease names (like "diabetes") and key laboratory numbers (like blood sugar or blood pressure readings). It determines if a disease is **Mild, Moderate, or Severe**.
2. **Step 2: Calculate Base Cost (The ML Model)**
   The system inputs your details into our trained computer program (`model.pkl`). This program predicts a "normal base cost" based on what average people of your age and habits pay.
3. **Step 3: Add/Subtract Surcharges (Underwriting Rules)**
   Real insurance companies increase or decrease your charges based on risk. The system calculates these changes:
   * **Location**: If you live in a expensive metro city (like Delhi or Mumbai), you pay **15% more**.
   * **Smoking**: If you smoke, you pay **40% more**.
   * **Age**: As you grow older (e.g. 50+), you pay **25% more**.
   * **BMI**: If you are overweight, you pay up to **20% more**.
   * **Diseases Found**: If you have a severe disease in your report, you pay **80% more** + a flat fee for treatment costs.
   * **Discounts**: If you choose to pay a portion of hospital bills yourself (called co-pay or deductibles), you get up to **45% discount**.
4. **Step 4: Pack the Final Plate**
   The waiter ([app.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/app.py)) gathers the final price, the list of diseases found, your health score, and recommendations, and displays them beautifully on your screen.

---

## 3. The Memory Notebook (SQLite Database)

To make sure the AI chatbot can converse normally, we use a simple database file called `chat_history.db`.
* **Chat Table**: Remembers the chat messages. When the user asks a question, the AI reads the last few messages from this table so it knows the conversation topic.
* **Profile Table**: Remembers your age, BMI, and predicted cost so the AI chatbot can reference it (e.g., if you ask *"How can I lower my Rs. 20,000 premium?"*, it knows your premium is Rs. 20,000).

---

## 4. Key Modularity Concepts (Answers for Teachers)

If a teacher asks **"Why is the code divided into so many files?"**, you can give these three simple reasons:

1. **Easy to Maintain (Single Job Rule)**:
   If the PDF reader fails, you only need to look at [medical_report_processor.py](file:///c:/Users/arvap/OneDrive/Documents/Desktop/mini project/src/mlproject/medical_report_processor.py). You don't have to touch the math code or UI code. It prevents breaking other parts of the project.
2. **Smart Backup System (Safety)**:
   If the Google Gemini AI gets disconnected or has no internet, the chatbot doesn't crash. It falls back to a smart local program that uses preset text rules to answer questions.
3. **Separate Training**:
   We train our model once in a separate program. The website does not waste computer power retraining the model every time a user visits. It simply loads the already-saved recipe (`model.pkl`).


🩺 MediSecure - System Architecture Report
This document outlines the complete technical architecture of the MediSecure Health Insurance Premium Calculator & Risk Engine. It explains the layout, data flows, and design decisions suitable for presentation to project mentors.

1. System Topology & Overview
MediSecure is built using a decoupled, modular Model-View-Controller (MVC) architecture. The backend acts as a request orchestrator (Controller), delegating calculations to specialized pipelines, engines, and NLP services.

Mermaid diagram
2. Layered Component Responsibilities
2.1 Presentation Layer (View)
File: templates/index.html
Technologies: HTML5, CSS3 (Vanilla Custom Styling), JavaScript.
Function: Renders the responsive user interface. It handles interactive validations, files uploads, chat modal states, and visualizes premium savings projections.
2.2 Orchestration Layer (Controller)
File: 
app.py
Technologies: Flask (Python).
Function: Acts as the routing manager. It accepts inputs from the user, forwards files to the PDF engine, runs the prediction pipeline, collects analytics outputs, and populates the template.
2.3 Core Engine Layer (Model/Services)
The business logic is split into highly cohesive, single-responsibility modules:

Module	File	Core Responsibility
Prediction Pipeline	
prediction_pipeline.py
Executes data formatting via CustomData, loads Random Forest models, and applies actuarial coefficient pricing adjustments.
Medical Report Processor	
medical_report_processor.py
Extracts text from PDF files using PyPDF2, parses blood readings via regular expressions, and identifies pre-existing medical conditions.
Health Risk Predictor	
health_risk_predictor.py
Computes profile-based health scores, forecasts future disease risks, and designs quarterly prevention milestone lists.
AI Chatbot Service	
gemini_chatbot.py
Communicates with the Google Gemini API, manages chat dialogue states, and falls back to a rule-based engine when offline.
3. Core Data Flow: Input to Calculation
When a user submits their profile and a medical report, the backend processes the data in the following sequential order:


[User Input Form]
        │
        ▼
[app.py (Controller)]
        │
        ├────────► [medical_report_processor.py]
        │               ├─ Extract text from PDF using PyPDF2
        │               ├─ Find disease indicators (16+ supported)
        │               ├─ Run RegEx for lab findings (glucose, HbA1c, BP, creatinine)
        │               └─ Output: disease_cost & disease_list
        │
        ├────────► [prediction_pipeline.py]
        │               ├─ Pack variables into CustomData DTO
        │               ├─ Transform features via preprocessor.pkl
        │               ├─ Predict base premium using model.pkl (Random Forest)
        │               ├─ Apply loading percentages (Age, BMI, Smoking, Zone, Co-pay, Deductibles)
        │               └─ Output: final_premium
        │
        ├────────► [health_risk_predictor.py]
        │               ├─ Compute Health Score (out of 100)
        │               ├─ Calculate potential annual savings from healthy habits
        │               └─ Generate timeline prevention milestone charts
        │
        └────────► Render index.html with all calculations
4. Underwriting & Pricing Formulas
The underwriting logic mathematically adjusts a base ML premium score using actuarial risk loadings:

Zone Modifiers: Adjusts premiums based on medical treatment costs in the user's state:
Zone A (Metro): 1.15× base (Delhi, Maharashtra, Karnataka, etc.)
Zone B (Tier 1): 1.00× base
Zone C (Tier 2/3): 0.88× base
Age & BMI Loadings:
Age: +8% for 35+, +15% for 40+, and +25% for 50+
BMI: +5% for 27+, +12% for 30+, and +20% for 35+
Smoking Loading: Flat +40% premium penalty.
Disease Surcharge (from PDF):
Surcharge multipliers: +15% (Mild), +35% (Moderate), and +80% (Severe)
Adding a confidence-weighted flat treatment expense (e.g., up to ₹1,80,000 for heart conditions).
5. Database Schema & Persistence
Chat logs and user profiles are stored locally in the SQLite database chat_history.db. This keeps context across requests.

5.1 Chat Messages Table (chat_messages)
Stores the conversation history for chatbot sessions.

Column	Type	Description
id	INTEGER (PK)	Auto-incrementing identifier.
session_id	TEXT	Unique session hash for the client.
role	TEXT	Role of the message creator (user, assistant, system).
message	TEXT	Raw text content of the message.
timestamp	DATETIME	Time the message was recorded.
5.2 User Profiles Table (user_profiles)
Stores the parsed profile data to contextually feed the AI chatbot.

Column	Type	Description
session_id	TEXT (PK)	Session identifier.
age	INTEGER	User's age.
sex	TEXT	User's gender.
bmi	REAL	Body Mass Index.
children	INTEGER	Dependent count.
smoker	TEXT	Smoking status (yes/no).
state	TEXT	Indian state of residence.
diseases	TEXT	JSON list of pre-existing conditions detected from the PDF.
predicted_cost	REAL	Final calculated annual premium.
created_at	DATETIME	Timestamp of entry creation.
6. Architecture Design Decisions (Modularity Checklist)
When mentors ask about the project's engineering quality, emphasize these points:

NOTE

Single Responsibility Principle (SRP) Every class and module has a single focus. For instance, 
medical_report_processor.py
 has no knowledge of web routing or database queries; it simply processes text streams.

TIP

Graceful Degradation In 
gemini_chatbot.py
, the GenAI connection is decoupled. If the Gemini API key is missing or is rate-limited, the system seamlessly activates a local rule-based response engine. The user experience remains uninterrupted.

IMPORTANT

Decoupled Training & Inference Training (retrain_model_real.py) is a standalone pipeline. The web app is completely decoupled from scikit-learn training operations; it runs purely in inference mode by consuming the serialized pipeline preprocessor.pkl and model.pkl. This reduces the CPU/RAM footprint of the production serve