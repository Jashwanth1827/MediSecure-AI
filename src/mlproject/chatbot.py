import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

INSURANCE_PLANS = {
    'basic_health': {
        'name': 'Basic Health Insurance',
        'coverage': '₹3-5 Lakhs',
        'premium_range': '₹5,000-15,000/year',
        'features': ['Hospitalization coverage', 'Day care procedures', 'Ambulance cover', 'Basic dental'),
        'best_for': ['Young individuals', 'Low-risk profiles', 'Budget-conscious'],
        'copay': '10-20%',
        'waiting_period': '30 days'
    },
    'standard_health': {
        'name': 'Standard Health Insurance',
        'coverage': '₹5-10 Lakhs',
        'premium_range': '₹15,000-30,000/year',
        'features': ['All Basic features', 'Maternity cover', 'Mental health coverage', 'Alternative treatments', 'Annual health checkup'],
        'best_for': ['Families', 'Middle-aged individuals', 'Pre-existing conditions after waiting period'],
        'copay': '5-10%',
        'waiting_period': '30 days, PED: 2-4 years'
    },
    'premium_health': {
        'name': 'Premium Health Insurance',
        'coverage': '₹10-25 Lakhs',
        'premium_range': '₹30,000-60,000/year',
        'features': ['All Standard features', 'No claim bonus', 'Restore benefit', 'International second opinion', 'Wellness programs', 'Zero copay options'],
        'best_for': ['Families with children', 'High-risk profiles', 'Comprehensive coverage seekers'],
        'copay': '0-5%',
        'waiting_period': '30 days, PED: 2 years'
    },
    'top_up_health': {
        'name': 'Top-Up Health Insurance',
        'coverage': '₹10-50 Lakhs (above deductible)',
        'premium_range': '₹3,000-10,000/year',
        'features': ['Super Mediclaim top-up', 'Low premium high coverage', 'Deductible required'],
        'best_for': ['Those with existing base coverage', 'Young healthy individuals', 'Cost-effective high coverage'],
        'copay': 'Based on deductible',
        'waiting_period': '30 days'
    },
    'critical_illness': {
        'name': 'Critical Illness Insurance',
        'coverage': '₹25 Lakhs-1 Crore (lump sum)',
        'premium_range': '₹10,000-50,000/year',
        'features': ['Lump sum payment on diagnosis', '36+ critical illnesses covered', 'Income replacement', 'Travel abroad treatment'],
        'best_for': ['Family breadwinners', 'High-risk occupations', 'Comprehensive protection seekers'],
        'copay': 'N/A (lump sum)',
        'waiting_period': '90 days'
    },
    'family_floater': {
        'name': 'Family Floater Health Insurance',
        'coverage': '₹5-50 Lakhs (shared)',
        'premium_range': '₹20,000-80,000/year',
        'features': ['Covers entire family', 'Spouse, children, parents', 'Maternity benefits', 'Newborn baby coverage'],
        'best_for': ['Married couples', 'Families with dependent children', 'Comprehensive family coverage'],
        'copay': '5-15%',
        'waiting_period': '30 days, PED: 2-4 years'
    },
    'senior_citizen': {
        'name': 'Senior Citizen Health Insurance',
        'coverage': '₹3-10 Lakhs',
        'premium_range': '₹20,000-50,000/year',
        'features': ['Pre-existing disease coverage', 'Higher entry age', 'Age-specific benefits', 'Dialysis cover'],
        'best_for': ['Ages 60+', 'Pre-existing conditions', 'Retirees'],
        'copay': '20-30%',
        'waiting_period': '30 days, PED: 1-2 years'
    },
    'coronavirus': {
        'name': 'COVID-19 Health Insurance',
        'coverage': '₹50,000-5 Lakhs',
        'premium_range': '₹500-3,000/year',
        'features': ['COVID-19 treatment', 'Home isolation cover', 'Oxygen support', 'Post-COVID complications'],
        'best_for': ['Everyone (add-on)', 'Additional COVID protection', 'Budget option'],
        'copay': 'Varies',
        'waiting_period': '15 days'
    }
}

DISEASE_RISK_FACTORS = {
    'diabetes': {'risk_level': 'high', 'recommendations': ['premium_health', 'critical_illness', 'senior_citizen']},
    'hypertension': {'risk_level': 'medium', 'recommendations': ['standard_health', 'premium_health', 'critical_illness']},
    'heart disease': {'risk_level': 'high', 'recommendations': ['premium_health', 'critical_illness', 'top_up_health']},
    'cancer': {'risk_level': 'critical', 'recommendations': ['critical_illness', 'premium_health', 'top_up_health']},
    'kidney disease': {'risk_level': 'high', 'recommendations': ['premium_health', 'critical_illness']},
    'liver disease': {'risk_level': 'high', 'recommendations': ['premium_health', 'critical_illness']},
    'respiratory': {'risk_level': 'medium', 'recommendations': ['standard_health', 'premium_health']},
    'mental health': {'risk_level': 'medium', 'recommendations': ['standard_health', 'premium_health']},
    'smoking': {'risk_level': 'high', 'recommendations': ['premium_health', 'critical_illness', 'top_up_health']},
    'obesity': {'risk_level': 'medium', 'recommendations': ['standard_health', 'premium_health']}
}

def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  role TEXT,
                  message TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_profiles
                 (session_id TEXT PRIMARY KEY,
                  age INTEGER,
                  sex TEXT,
                  bmi REAL,
                  children INTEGER,
                  smoker TEXT,
                  state TEXT,
                  diseases TEXT,
                  predicted_cost REAL,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_message(session_id: str, role: str, message: str):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO chat_messages (session_id, role, message) VALUES (?, ?, ?)",
              (session_id, role, message))
    conn.commit()
    conn.close()

def get_chat_history(session_id: str, limit: int = 10) -> List[Dict]:
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT role, message, timestamp FROM chat_messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
              (session_id, limit))
    rows = c.fetchall()
    conn.close()
    return [{'role': r[0], 'message': r[1], 'timestamp': r[2]} for r in reversed(rows)]

def save_user_profile(session_id: str, profile: Dict):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO user_profiles 
                 (session_id, age, sex, bmi, children, smoker, state, diseases, predicted_cost)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (session_id, profile.get('age'), profile.get('sex'), profile.get('bmi'),
               profile.get('children'), profile.get('smoker'), profile.get('state'),
               json.dumps(profile.get('diseases', [])), profile.get('predicted_cost', 0)))
    conn.commit()
    conn.close()

def get_user_profile(session_id: str) -> Optional[Dict]:
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_profiles WHERE session_id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'age': row[1], 'sex': row[2], 'bmi': row[3], 'children': row[4],
            'smoker': row[5], 'state': row[6], 'diseases': json.loads(row[7]) if row[7] else [],
            'predicted_cost': row[8]
        }
    return None

def recommend_insurance(profile: Dict) -> List[Dict]:
    recommendations = []
    diseases = profile.get('diseases', [])
    age = profile.get('age', 30)
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    bmi = profile.get('bmi', 25)
    children = profile.get('children', 0)
    
    base_score = 1.0
    
    if age > 60:
        recommendations.append(INSURANCE_PLANS['senior_citizen'])
        base_score += 0.2
    elif age > 45:
        base_score += 0.1
    
    if smoker:
        base_score += 0.3
        recommendations.append(INSURANCE_PLANS['critical_illness'])
        if INSURANCE_PLANS['premium_health'] not in recommendations:
            recommendations.append(INSURANCE_PLANS['premium_health'])
    
    if bmi > 30:
        base_score += 0.2
    
    for disease in diseases:
        disease_lower = disease.lower()
        for risk_key, risk_info in DISEASE_RISK_FACTORS.items():
            if risk_key in disease_lower:
                if risk_info['risk_level'] == 'critical':
                    recommendations.insert(0, INSURANCE_PLANS['critical_illness'])
                    recommendations.insert(0, INSURANCE_PLANS['premium_health'])
                elif risk_info['risk_level'] == 'high':
                    if INSURANCE_PLANS['critical_illness'] not in recommendations:
                        recommendations.insert(0, INSURANCE_PLANS['critical_illness'])
                    if INSURANCE_PLANS['premium_health'] not in recommendations:
                        recommendations.insert(0, INSURANCE_PLANS['premium_health'])
                else:
                    if INSURANCE_PLANS['standard_health'] not in recommendations:
                        recommendations.append(INSURANCE_PLANS['standard_health'])
    
    if children > 0:
        if INSURANCE_PLANS['family_floater'] not in recommendations:
            recommendations.append(INSURANCE_PLANS['family_floater'])
    
    seen = set()
    unique_recs = []
    for rec in recommendations:
        if rec['name'] not in seen:
            seen.add(rec['name'])
            unique_recs.append(rec)
    
    if len(unique_recs) < 2:
        if age < 40:
            unique_recs.append(INSURANCE_PLANS['basic_health'])
        else:
            unique_recs.append(INSURANCE_PLANS['standard_health'])
        if smoker or len(diseases) > 0:
            unique_recs.append(INSURANCE_PLANS['top_up_health'])
    
    return unique_recs[:4]

def generate_insurance_suggestion(profile: Dict) -> str:
    recommendations = recommend_insurance(profile)
    
    age = profile.get('age', 30)
    state = profile.get('state', 'Unknown')
    diseases = profile.get('diseases', [])
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    
    suggestion = f"## 🏥 Insurance Recommendation for You\n\n"
    suggestion += f"Based on your profile:\n"
    suggestion += f"- **Age:** {age} years\n"
    suggestion += f"- **Location:** {state.title()}\n"
    suggestion += f"- **Health Conditions:** {', '.join([d.title() for d in diseases]) if diseases else 'None reported'}\n"
    suggestion += f"- **Smoker:** {'Yes' if smoker else 'No'}\n\n"
    
    suggestion += "---\n\n"
    suggestion += "### Recommended Plans:\n\n"
    
    for i, plan in enumerate(recommendations, 1):
        suggestion += f"**{i}. {plan['name']}**\n"
        suggestion += f"   - Coverage: {plan['coverage']}\n"
        suggestion += f"   - Premium: {plan['premium_range']}\n"
        suggestion += f"   - Best For: {', '.join(plan['best_for'])}\n"
        suggestion += f"   - Key Features: {', '.join(plan['features'][:3])}\n\n"
    
    return suggestion

def get_health_tip(disease: str = None, age: int = 30) -> str:
    tips = {
        'general': [
            "Regular health checkups can catch issues early.",
            "Maintain a balanced diet rich in fruits and vegetables.",
            "Exercise at least 30 minutes daily.",
            "Stay hydrated - drink 8 glasses of water daily.",
            "Get adequate sleep (7-8 hours for adults).",
            "Manage stress through meditation or hobbies.",
            "Avoid smoking and limit alcohol consumption.",
            "Keep your BMI between 18.5 and 24.9."
        ],
        'diabetes': [
            "Monitor blood sugar levels regularly.",
            "Follow a low-glycemic diet.",
            "Include fiber-rich foods in your diet.",
            "Exercise helps control blood sugar.",
            "Don't skip meals, especially breakfast."
        ],
        'hypertension': [
            "Reduce sodium intake to less than 2,300mg/day.",
            "Potassium-rich foods help balance sodium.",
            "Regular aerobic exercise lowers BP.",
            "Limit alcohol and caffeine.",
            "Manage stress effectively."
        ],
        'heart': [
            "Include omega-3 rich foods (fish, nuts).",
            "Quit smoking immediately.",
            "Regular ECG checkups recommended.",
            "Control cholesterol levels.",
            "Maintain healthy weight."
        ]
    }
    
    import random
    if disease:
        disease_lower = disease.lower()
        for key in tips:
            if key in disease_lower:
                return random.choice(tips[key])
    return random.choice(tips['general'])

init_db()
