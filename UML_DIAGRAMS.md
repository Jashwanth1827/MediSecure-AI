# 📊 MediSecure-AI - System Architecture & UML Diagrams

This document contains visual diagrams mapping out the high-level system architecture, the detailed object-oriented structure (UML Class Diagram), and the runtime execution flow (UML Sequence Diagram) of the MediSecure-AI project.

---

## 1. System Architecture Diagram

```mermaid
graph TB
    subgraph ClientLayer [Client Layer (Browser)]
        UI[index.html / Custom CSS / JavaScript]
        Interaction[Form Calculator, SVG Progress Rings, AI Warnings & Adjuster Panels]
    end

    subgraph ServerLayer [Server Layer - app.py]
        App[Flask Application Context]
        Routes[API Routes: /, /chat, /google-fit/connect, /google-fit/sync]
        Logger[logger.py - Event Logging]
    end

    subgraph ServiceLayer [Business Logic & Service Layer]
        PDF[medical_report_processor.py<br/>PDF Extractor & Disease Underwriter]
        ML[prediction_pipeline.py<br/>ML Inference & Premium Modifiers]
        Risk[health_risk_predictor.py<br/>Health Diagnostics & Adaptive Workout Planner]
        Fit[google_fit.py<br/>OAuth 2.0 Client & REST Telemetry Fetcher]
        Chat[gemini_chatbot.py<br/>GenAI Dialogue & local fallback]
    end

    subgraph DataLayer [Data & Models Layer]
        DB[(chat_history.db - SQLite Database)]
        ModelStore[model.pkl & preprocessor.pkl<br/>Random Forest ML Pipeline]
        Gemini[Google Gemini API]
        FitAPI[Google Fitness REST API]
    end

    %% Client and Server
    UI <-->|HTTP POST / JSON / Sync| App

    %% Server and Services
    App -->|Processes PDF reports| PDF
    App -->|Calculates ML premium| ML
    App -->|Triggers risk diagnostics & adaptive plans| Risk
    App -->|Requests OAuth code exchanges & syncs data| Fit
    App -->|Directs conversation streams| Chat

    %% Services and Data
    ML -->|Inference data preprocessing| ModelStore
    Fit <-->|Fetches steps, sleep, water, active time| FitAPI
    Chat -->|Saves dialogue threads & user profiles| DB
    Chat <-->|Invokes GenAI client| Gemini
```

---

## 2. UML Class Diagram

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
        +str severity
        +calculate_premium_modifiers() Dict
        +get_data_as_data_frame() DataFrame
    }
    
    class PredictPipeline {
        +predict(features DataFrame) ndarray
    }

    class GoogleFitHelper {
        <<google_fit.py>>
        +get_fit_auth_url(client_id) str
        +exchange_fit_code(code, client_id, client_secret) Dict
        +refresh_fit_token(refresh_token, client_id, client_secret) Dict
        +fetch_fit_metrics(access_token) Dict
        +get_user_email(access_token) str
    }

    class FlaskController {
        <<app.py>>
        +predict_datapoint() html
        +chat() json
        +google_fit_connect() redirect
        +google_fit_callback() redirect
        +google_fit_sync() json
        +google_fit_disconnect() json
    }

    %% Relationships
    FlaskController ..> CustomData : creates
    FlaskController ..> PredictPipeline : executes
    FlaskController ..> GoogleFitHelper : invokes
```

---

## 3. UML Sequence Diagram: Google Fit Sync & Live Underwrite

This diagram tracks the runtime execution flow when a user connects their account and clicks **Sync Now** to dynamically recalculate their premium based on behavioral telemetry:

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Browser (index.html)
    participant App as Flask Server (app.py)
    participant Fit as google_fit.py
    participant FitAPI as Google Fitness REST API
    participant DB as SQLite (chat_history.db)

    User->>App: Click 'Sync Now' (HTTP GET /google-fit/sync)
    activate App
    
    rect rgb(240, 240, 240)
        Note over App, FitAPI: Step 1: Real-Time Telemetry Retrieval
        App->>Fit: fetch_fit_metrics(access_token)
        activate Fit
        Fit->>FitAPI: HTTP POST /dataset:aggregate (Steps, Hydration, Active time)
        FitAPI-->>Fit: Return aggregation values
        Fit->>FitAPI: HTTP GET /sessions (Sleep sessions)
        FitAPI-->>Fit: Return sleep session durations
        Fit-->>App: Return combined metrics dict (steps, sleep, water, active time)
        deactivate Fit
    end

    rect rgb(230, 245, 255)
        Note over App, DB: Step 2: Session Profile Lookup
        App->>DB: get_user_profile(session_id)
        DB-->>App: Return user_profile dict (base premium, pre-existing diseases)
    end

    rect rgb(240, 255, 240)
        Note over App, App: Step 3: Actuarial Underwriting & Alerts Compilation
        App->>App: Calculate dynamic premium adjuster discount (up to 15%)
        App->>App: Cross-reference metrics with chronic diseases (Hypertension, Diabetes)
        App->>App: Compile adaptive recovery or booster workouts based on target deficits
    end

    App-->>User: HTTP 200 OK JSON (metrics, adjuster stats, clinical alerts, adaptive workout plan)
    deactivate App
    
    Note over User: UI animates SVG circular progress gauges and renders Adjuster, Warnings, and Planner cards
```
