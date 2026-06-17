# =====================================================================
# ARCHITECTURE ROLE: GOOGLE FIT CLIENT & OAUTH ORCHESTRATOR
# =====================================================================
# This module implements the Google Fit REST API integration. It manages
# the OAuth2 lifecycle (generating links, exchanging codes, refreshing tokens)
# and retrieves steps, sleep, hydration, and active time.
# =====================================================================

import urllib.parse
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
FITNESS_AGGREGATE_URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
FITNESS_SESSIONS_URL = "https://www.googleapis.com/fitness/v1/users/me/sessions"

SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.sleep.read",
    "https://www.googleapis.com/auth/fitness.body.read",
    "https://www.googleapis.com/auth/userinfo.email"
]

def get_fit_auth_url(client_id: str, redirect_uri: str) -> str:
    """Generates the Google OAuth 2.0 authorization URL."""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{OAUTH_AUTH_URL}?{urllib.parse.urlencode(params)}"

def exchange_fit_code(code: str, client_id: str, client_secret: str, redirect_uri: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Exchanges authorization code for access and refresh tokens.
    Returns (token_dict, error_message).
    """
    payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    try:
        response = requests.post(OAUTH_TOKEN_URL, data=payload, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            # Add absolute expiry timestamp
            if "expires_in" in token_data:
                token_data["expires_at"] = int(time.time()) + token_data["expires_in"]
            return token_data, None
        return None, response.text
    except Exception as e:
        return None, str(e)

def refresh_fit_token(refresh_token: str, client_id: str, client_secret: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Refreshes the access token using the refresh token."""
    payload = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    try:
        response = requests.post(OAUTH_TOKEN_URL, data=payload, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            if "expires_in" in token_data:
                token_data["expires_at"] = int(time.time()) + token_data["expires_in"]
            # Ensure we keep the refresh token if Google didn't return a new one
            if "refresh_token" not in token_data:
                token_data["refresh_token"] = refresh_token
            return token_data, None
        return None, response.text
    except Exception as e:
        return None, str(e)

def get_user_email(access_token: str) -> Optional[str]:
    """Fetches user email from Google Userinfo API."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        res = requests.get(USER_INFO_URL, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get("email")
    except Exception:
        pass
    return None

def fetch_fit_metrics(access_token: str) -> Dict:
    """Queries the Google Fit API for steps, sleep, active time, and hydration for today."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Calculate start of today (local time based on server, ideally user timezone but we'll use local day)
    now = datetime.now()
    midnight = datetime(now.year, now.month, now.day)
    start_time_ms = int(midnight.timestamp() * 1000)
    end_time_ms = int(now.timestamp() * 1000)
    
    # Handle exact midnight edge case
    if start_time_ms >= end_time_ms:
        start_time_ms = end_time_ms - 60000
        
    metrics = {
        "steps": 0,
        "sleep_hours": 0.0,
        "water_liters": 0.0,
        "active_minutes": 0,
        "error": None
    }
    
    # 1. Fetch Steps
    steps_payload = {
        "aggregateBy": [{
            "dataTypeName": "com.google.step_count.delta",
            "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
        }],
        "bucketByTime": { "durationMillis": 86400000 },
        "startTimeMillis": start_time_ms,
        "endTimeMillis": end_time_ms
    }
    try:
        res = requests.post(FITNESS_AGGREGATE_URL, headers=headers, json=steps_payload, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for bucket in data.get("bucket", []):
                for dataset in bucket.get("dataset", []):
                    for point in dataset.get("point", []):
                        for val in point.get("value", []):
                            metrics["steps"] += val.get("intVal", 0)
    except Exception as e:
        metrics["error"] = f"Steps fetch failed: {str(e)}"
        
    # 2. Fetch Sleep (via sessions in last 24 hours to capture last night's sleep)
    sleep_start = now - timedelta(days=1)
    sleep_start_iso = sleep_start.isoformat() + "Z"
    sleep_end_iso = now.isoformat() + "Z"
    try:
        params = {
            "startTime": sleep_start_iso,
            "endTime": sleep_end_iso,
            "activityType": 72 # Google Fit activity type for Sleep
        }
        res = requests.get(FITNESS_SESSIONS_URL, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            total_sleep_ms = 0
            for session in data.get("session", []):
                start = int(session.get("startTimeMillis", 0))
                end = int(session.get("endTimeMillis", 0))
                total_sleep_ms += (end - start)
            metrics["sleep_hours"] = round(total_sleep_ms / (1000 * 60 * 60), 2)
    except Exception as e:
        if not metrics["error"]:
            metrics["error"] = f"Sleep fetch failed: {str(e)}"

    # 3. Fetch Hydration (Water in Liters)
    water_payload = {
        "aggregateBy": [{
            "dataTypeName": "com.google.hydration",
            "dataSourceId": "derived:com.google.hydration:com.google.android.gms:merged"
        }],
        "bucketByTime": { "durationMillis": 86400000 },
        "startTimeMillis": start_time_ms,
        "endTimeMillis": end_time_ms
    }
    try:
        res = requests.post(FITNESS_AGGREGATE_URL, headers=headers, json=water_payload, timeout=5)
        if res.status_code == 200:
            data = res.json()
            total_water_ml = 0.0
            for bucket in data.get("bucket", []):
                for dataset in bucket.get("dataset", []):
                    for point in dataset.get("point", []):
                        for val in point.get("value", []):
                            total_water_ml += val.get("fpVal", 0.0)
            # Google Fit records hydration in Liters, so aggregate directly
            metrics["water_liters"] = round(total_water_ml, 2)
    except Exception as e:
        if not metrics["error"]:
            metrics["error"] = f"Hydration fetch failed: {str(e)}"

    # 4. Fetch Active Minutes
    active_payload = {
        "aggregateBy": [{
            "dataTypeName": "com.google.active_minutes",
            "dataSourceId": "derived:com.google.active_minutes:com.google.android.gms:merge_active_minutes"
        }],
        "bucketByTime": { "durationMillis": 86400000 },
        "startTimeMillis": start_time_ms,
        "endTimeMillis": end_time_ms
    }
    try:
        res = requests.post(FITNESS_AGGREGATE_URL, headers=headers, json=active_payload, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for bucket in data.get("bucket", []):
                for dataset in bucket.get("dataset", []):
                    for point in dataset.get("point", []):
                        for val in point.get("value", []):
                            metrics["active_minutes"] += val.get("intVal", 0)
    except Exception as e:
        # Fallback to general activity duration if active_minutes not supported
        activity_payload = {
            "aggregateBy": [{
                "dataTypeName": "com.google.activity.segment",
                "dataSourceId": "derived:com.google.activity.segment:com.google.android.gms:merge_activity_segments"
            }],
            "bucketByTime": { "durationMillis": 86400000 },
            "startTimeMillis": start_time_ms,
            "endTimeMillis": end_time_ms
        }
        try:
            res = requests.post(FITNESS_AGGREGATE_URL, headers=headers, json=activity_payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                total_duration_ms = 0
                for bucket in data.get("bucket", []):
                    for dataset in bucket.get("dataset", []):
                        for point in dataset.get("point", []):
                            # Exclude sleeping (72) and inactive (3) types
                            act_type = point.get("value", [{}])[0].get("intVal", 0)
                            if act_type not in [3, 72]:
                                start = int(point.get("startTimeNanos", 0)) // 1000000
                                end = int(point.get("endTimeNanos", 0)) // 1000000
                                total_duration_ms += (end - start)
                metrics["active_minutes"] = int(total_duration_ms / (1000 * 60))
        except Exception:
            if not metrics["error"]:
                metrics["error"] = "Active minutes fetch failed"

    return metrics
