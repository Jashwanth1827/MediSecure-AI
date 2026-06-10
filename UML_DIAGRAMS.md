# 📊 MediSecure - System Architecture & UML Diagrams

This document contains visual diagrams mapping out the high-level system architecture, the detailed object-oriented structure (UML Class Diagram), and the runtime execution flow (UML Sequence Diagram) of the MediSecure project.

---

## 1. System Architecture Diagram
This diagram shows how different layers of the system interact, from the web UI down to the data files and external APIs.

```mermaid
graph TB
    subgraph ClientLayer [Client Layer (Browser)]
        UI[index.html / Custom CSS / JavaScript]
        Interaction[Form Submission, File Upload, Chat Widget]
    end

    subgraph ServerLayer [Server Layer - app.py]
        App[Flask Application Context]
        Routes[API Routes: /, /chat, /api/profile, /api/compare-plans]
        Logger[logger.py - Event Logging]
        Ex[exception.py - Custom Error Handling]
    end

    subgraph ServiceLayer [Business Logic & Service Layer]
        PDF[medical_report_processor.py<br/>PDF Extractor & Disease Underwriter]
        ML[prediction_pipeline.py<br/>ML Inference & Actuarial Surcharge Calculator]
        Risk[health_risk_predictor.py<br/>Health Diagnostics & Prevention Planner]
        Chat[gemini_chatbot.py<br/>Chatbot Context & AI Dialogue Manager]
    end

    subgraph DataLayer [Data & Models Layer]
        DB[(chat_history.db - SQLite Database)]
        ModelStore[model.pkl & preprocessor.pkl<br/>Serialized Random Forest & Column Transformers]
        Gemini[Google Gemini AI API<br/>gemini-2.0-flash Model]
    end

    %% Client and Server Interaction
    UI <-->|HTTP POST / JSON Requests| App

    %% Server and Services
    App -->|Reads uploaded PDF reports| PDF
    App -->|Instantiates CustomData DTO| ML
    App -->|Calculates scores & prevention plans| Risk
    App -->|Delegates conversation context| Chat

    %% Services and Data
    ML -->|Unpickles and transforms inputs| ModelStore
    Chat -->|Stores message streams & user profiles| DB
    Chat <-->|Invokes GenAI client| Gemini
```

---

## 2. UML Class Diagram
This diagram shows the static structure of classes, their fields, methods, and relationships.

```mermaid
classDiagram
    class CustomData {
        +int age
        +str sex
        +float bmi
        +int children
        +str smoker
        +str state
        +str sum_insured
        +str policy_term
        +str room_type
        +str deductible
        +str copay
        +str ncb
        +str riders
        +float disease_cost
        +int disease_count
        +str severity
        +calculate_premium_modifiers() Dict
        +get_data_as_data_frame() DataFrame
    }
    
    class PredictPipeline {
        +predict(features DataFrame) ndarray
    }

    class CustomException {
        +str error_message
        +__str__() str
    }

    class Exception {
        <<Built-in Class>>
    }

    class FlaskController {
        <<app.py>>
        +predict_datapoint() html
        +chat() json
        +chat_history() json
        +clear_chat() json
        +api_profile() json
        +compare_plans() json
    }

    %% Relationships
    CustomException --|> Exception : inherits
    FlaskController ..> CustomData : creates
    FlaskController ..> PredictPipeline : executes
    PredictPipeline ..> CustomException : raises
    CustomData ..> CustomException : raises
```

---

## 3. UML Sequence Diagram
This diagram tracks a single, complete execution cycle: when a user clicks the **Calculate Premium** button on the UI, uploading a medical report along with their health parameters.

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Browser (index.html)
    participant App as Flask Server (app.py)
    participant PDF as medical_report_processor.py
    participant Pipeline as prediction_pipeline.py
    participant Risk as health_risk_predictor.py
    participant DB as SQLite Database (chat_history.db)

    User->>App: HTTP POST / (Profile inputs + PDF File stream)
    activate App
    
    rect rgb(245, 245, 245)
        Note over App, PDF: Step 1: Medical Document Underwriting
        App->>PDF: process_medical_report(temp_pdf_filepath)
        activate PDF
        PDF->>PDF: extract_text_from_pdf()
        PDF->>PDF: extract_lab_values() (blood sugar, BP, creatinine)
        PDF->>PDF: detect_diseases() & detect_severity()
        PDF->>PDF: calculate_disease_cost()
        PDF-->>App: Return (disease_cost, diseases_found, severity, report_summary)
        deactivate PDF
    end

    rect rgb(235, 245, 255)
        Note over App, Pipeline: Step 2: Machine Learning Prediction & Loadings
        App->>Pipeline: CustomData(age, sex, bmi, state, disease_cost, severity, etc.)
        activate Pipeline
        Pipeline->>Pipeline: calculate_premium_modifiers() (Age/BMI/Smoker/Zone Loadings)
        Pipeline->>Pipeline: load model.pkl & preprocessor.pkl
        Pipeline->>Pipeline: model.predict(scaled_features)
        Pipeline->>Pipeline: calculate_final_premium(base_predicted, modifiers, disease_cost)
        Pipeline-->>App: Return final_calculated_premium
        deactivate Pipeline
    end

    rect rgb(245, 255, 245)
        Note over App, Risk: Step 3: Diagnostic Scoring & Preventative Planning
        App->>Risk: calculate_health_score(profile, diseases, severity)
        activate Risk
        App->>Risk: predict_health_risks(profile, diseases, severity)
        App->>Risk: generate_prevention_plan(profile, diseases, severity)
        Risk-->>App: Return (health_score, future_risks, milestone_plan)
        deactivate Risk
    end

    rect rgb(255, 245, 245)
        Note over App, DB: Step 4: Persistent Context Saving
        App->>DB: save_user_profile(session_id, profile)
    end

    App-->>User: HTTP 200 OK (Renders index.html with calculations, savings, and chatbot initialized)
    deactivate App
```
