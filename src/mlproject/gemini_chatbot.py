# =====================================================================
# ARCHITECTURE ROLE: CONVERSATIONAL AI & USER HISTORY SERVICE (Chatbot)
# =====================================================================
# This module implements the natural language interface of MediSecure.
# It handles Google Gemini API configurations, session message logging 
# (persisting user histories to SQLite database `chat_history.db`), and
# provides a robust rule-based backup response system (local fallback)
# when the Gemini API is offline or unconfigured.
#
# Modularity benefits:
# 1. Isolates Generative AI vendor library calls (google-genai).
# 2. Separates user session profiles and SQLite transactional database schema
#    operations from the web server endpoints in app.py.
# =====================================================================

import os
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

from dotenv import load_dotenv

DB_PATH = os.environ.get('CHATBOT_DB_PATH', 'chat_history.db')

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(project_root, '.env'))

from src.mlproject.insurance_company_data import (
    INSURANCE_COMPANIES,
    get_all_companies,
    get_all_plans,
    filter_plans
)

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google GenAI not installed. Run: pip install google-genai")

INSURANCE_PLANS = {
    'basic_health': {
        'name': 'Basic Health Insurance',
        'coverage': '₹3-5 Lakhs',
        'premium_range': '₹5,000-15,000/year',
        'features': ['Hospitalization coverage', 'Day care procedures', 'Ambulance cover'],
        'best_for': ['Young individuals', 'Low-risk profiles', 'Budget-conscious']
    },
    'standard_health': {
        'name': 'Standard Health Insurance',
        'coverage': '₹5-10 Lakhs',
        'premium_range': '₹15,000-30,000/year',
        'features': ['All Basic features', 'Maternity cover', 'Mental health coverage', 'Alternative treatments'],
        'best_for': ['Families', 'Middle-aged individuals', 'Pre-existing conditions after waiting period']
    },
    'premium_health': {
        'name': 'Premium Health Insurance',
        'coverage': '₹10-25 Lakhs',
        'premium_range': '₹30,000-60,000/year',
        'features': ['All Standard features', 'No claim bonus', 'Restore benefit', 'International second opinion'],
        'best_for': ['Families with children', 'High-risk profiles', 'Comprehensive coverage seekers']
    },
    'critical_illness': {
        'name': 'Critical Illness Insurance',
        'coverage': '₹25 Lakhs-1 Crore (lump sum)',
        'premium_range': '₹10,000-50,000/year',
        'features': ['Lump sum payment on diagnosis', '36+ critical illnesses covered', 'Income replacement'],
        'best_for': ['Family breadwinners', 'High-risk occupations', 'Comprehensive protection seekers']
    },
    'family_floater': {
        'name': 'Family Floater Health Insurance',
        'coverage': '₹5-50 Lakhs (shared)',
        'premium_range': '₹20,000-80,000/year',
        'features': ['Covers entire family', 'Spouse, children, parents', 'Maternity benefits'],
        'best_for': ['Married couples', 'Families with dependent children', 'Comprehensive family coverage']
    },
    'senior_citizen': {
        'name': 'Senior Citizen Health Insurance',
        'coverage': '₹3-10 Lakhs',
        'premium_range': '₹20,000-50,000/year',
        'features': ['Pre-existing disease coverage', 'Higher entry age', 'Dialysis cover'],
        'best_for': ['Ages 60+', 'Pre-existing conditions', 'Retirees']
    },
    'top_up_health': {
        'name': 'Top-Up Health Insurance',
        'coverage': '₹10-50 Lakhs (above deductible)',
        'premium_range': '₹3,000-10,000/year',
        'features': ['Super Mediclaim top-up', 'Low premium high coverage', 'Deductible required'],
        'best_for': ['Those with existing base coverage', 'Young healthy individuals', 'Cost-effective high coverage']
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

GEMINI_CLIENT = None
GEMINI_MODEL = None
GEMINI_CONFIGURED = False

def configure_gemini():
    global GEMINI_CLIENT, GEMINI_MODEL, GEMINI_CONFIGURED
    
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    
    if not api_key:
        print("Warning: GEMINI_API_KEY not set. Chatbot will use local mode.")
        GEMINI_CONFIGURED = False
        return False
    
    try:
        GEMINI_CLIENT = genai.Client(api_key=api_key)
        GEMINI_MODEL = "gemini-2.0-flash"
        GEMINI_CONFIGURED = True
        print("Gemini AI configured successfully!")
        return True
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        GEMINI_CONFIGURED = False
        return False

def update_gemini_key(new_key: str) -> bool:
    """Update Gemini API key at runtime and reconfigure the client.
    Returns True if configuration succeeds, False otherwise.
    """
    global GEMINI_CLIENT, GEMINI_MODEL, GEMINI_CONFIGURED
    if not new_key:
        return False
    os.environ['GEMINI_API_KEY'] = new_key
    # Persist to .env for testing convenience
    try:
        import pathlib
        project_root = pathlib.Path(__file__).resolve().parents[3]
        env_path = project_root / '.env'
        if env_path.exists():
            text = env_path.read_text()
            if 'GEMINI_API_KEY=' in text:
                text = '\n'.join([l if not l.startswith('GEMINI_API_KEY=') else f'GEMINI_API_KEY={new_key}' for l in text.splitlines()])
            else:
                text = text + f"\nGEMINI_API_KEY={new_key}\n"
            env_path.write_text(text)
        else:
            env_path.write_text(f"GEMINI_API_KEY={new_key}\n")
    except Exception:
        pass
    # Attempt to reconfigure with the new key
    return configure_gemini()

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO chat_messages (session_id, role, message) VALUES (?, ?, ?)",
              (session_id, role, message))
    conn.commit()
    conn.close()

def get_chat_history(session_id: str, limit: int = 20) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT role, message, timestamp FROM chat_messages 
                 WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?""",
              (session_id, limit))
    rows = c.fetchall()
    conn.close()
    return [{'role': r[0], 'message': r[1], 'timestamp': r[2]} for r in reversed(rows)]

def save_user_profile(session_id: str, profile: Dict):
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
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
    
    if age > 60:
        recommendations.append(INSURANCE_PLANS['senior_citizen'])
    elif age > 45:
        recommendations.append(INSURANCE_PLANS['standard_health'])
    
    if smoker:
        recommendations.append(INSURANCE_PLANS['critical_illness'])
        if INSURANCE_PLANS['premium_health'] not in recommendations:
            recommendations.append(INSURANCE_PLANS['premium_health'])
    
    if bmi > 30:
        recommendations.append(INSURANCE_PLANS['standard_health'])
    
    for disease in diseases:
        disease_lower = disease.lower()
        for risk_key, risk_info in DISEASE_RISK_FACTORS.items():
            if risk_key in disease_lower:
                for rec_name in risk_info['recommendations']:
                    rec = INSURANCE_PLANS.get(rec_name)
                    if rec and rec not in recommendations:
                        recommendations.insert(0, rec)
    
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
        unique_recs.append(INSURANCE_PLANS['basic_health'])
    
    return unique_recs[:4]

def get_system_prompt(profile: Optional[Dict] = None) -> str:
    profile_context = ""
    if profile:
        profile_context = f"""
User Profile:
- Age: {profile.get('age', 'Not specified')} years
- Location: {profile.get('state', 'Not specified').title() if profile.get('state') else 'Not specified'}
- Health Conditions: {', '.join([d.title() for d in profile.get('diseases', [])]) if profile.get('diseases') else 'None reported'}
- Smoker: {'Yes' if profile.get('smoker', '').lower() == 'yes' else 'No'}
- BMI: {profile.get('bmi', 'Not specified')}
- Dependents: {profile.get('children', 0)}
- Predicted Insurance Cost: Rs.{profile.get('predicted_cost', 0):,.2f}
"""

    company_list = ""
    for cid, cdata in INSURANCE_COMPANIES.items():
        company_list += f"- {cdata['name']} (CSR: {cdata['claim_settlement_ratio']}, Network: {cdata['network_hospitals']} hospitals)\n"

    return f"""You are MediSecure AI, a helpful health insurance assistant built into an insurance premium prediction platform. You assist users in understanding health insurance premiums, comparing plans, and making informed coverage decisions.

YOUR ROLE:
- Help users understand how their health profile (age, BMI, smoking, diseases) affects their premium
- Compare real insurance plans from Indian companies: HDFC ERGO, ICICI Lombard, Bajaj Allianz, Star Health, Niva Bupa, Care Health, Reliance General, ManipalCigna, National Insurance, and Oriental Insurance
- Explain insurance terms: deductibles, NCB, co-pay, riders, sum insured, waiting periods
- Give personalized recommendations based on the user's profile
- Suggest ways to reduce premiums through lifestyle changes or policy adjustments
- Guide users through the claim process

COMMUNICATION STYLE:
- Friendly, professional, and consultative
- Use clear language - avoid jargon unless explaining it
- Always reference real company names and specific data (CSR, network hospitals, premiums)
- Use bullet points and tables for comparisons
- Be concise but thorough
- Always stay focused on health insurance topics

KEY METRICS TO REFERENCE:
- Claim Settlement Ratio (CSR) - higher is better
- Network hospitals - more hospitals = better cashless access
- Waiting periods for pre-existing diseases
- Premium amounts and value for money

IMPORTANT GUIDELINES:
- If the user asks about something unrelated to health insurance, politely redirect them back to insurance topics
- Always identify yourself as the MediSecure AI Insurance Assistant when asked
- If you don't know specific data, give general guidance and suggest the user fill in their profile for personalized results

{profile_context}

Available Insurance Companies:
{company_list}

Always be helpful, accurate, and focused on health insurance. Recommend specific plans from specific companies when possible."""

def chat_with_gemini(message: str, session_id: str) -> str:
    if not GEMINI_CONFIGURED or GEMINI_CLIENT is None:
        return get_local_response(message, session_id)
    
    try:
        profile = get_user_profile(session_id)
        system_prompt = get_system_prompt(profile)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT role, message FROM chat_messages 
                     WHERE session_id = ? AND role IN ('user', 'assistant')
                     ORDER BY id DESC LIMIT 10""",
                  (session_id,))
        rows = c.fetchall()
        conn.close()
        
        conversation_history = []
        for row in reversed(rows):
            role = row[0]
            msg = row[1]
            if role == 'user':
                conversation_history.append({'role': 'user', 'parts': [{'text': msg}]})
            elif role == 'assistant':
                conversation_history.append({'role': 'model', 'parts': [{'text': msg}]})
        
        if len(conversation_history) == 0 or conversation_history[-1]['role'] != 'user':
            conversation_history.append({'role': 'user', 'parts': [{'text': message}]})
        
        response = GEMINI_CLIENT.models.generate_content(
            model=GEMINI_MODEL,
            contents=conversation_history,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=2048,
            )
        )
        
        if response.text:
            return response.text
        return get_local_response(message, session_id)
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return get_local_response(message, session_id)

def get_local_response(message: str, session_id: str) -> str:
    profile = get_user_profile(session_id)
    message_lower = message.lower().strip()
    
    def has_profile():
        return profile and profile.get('age')
    
    def profile_summary():
        if not has_profile():
            return ""
        p = profile
        s = "Based on your profile (Age: {}, BMI: {}, ".format(p.get('age','?'), p.get('bmi','?'))
        s += "Smoker: {}, ".format('Yes' if p.get('smoker','no').lower()=='yes' else 'No')
        s += "State: {})".format(p.get('state','?').title())
        if p.get('diseases'):
            s += " with health conditions: {}".format(', '.join([d.title() for d in p['diseases']]))
        if p.get('predicted_cost'):
            s += "\nYour estimated premium: Rs.{:,.2f}/year".format(p['predicted_cost'])
        return s
    
    greetings = ['hi', 'hello', 'hey', 'howdy', 'greetings', 'good morning', 'good evening', 'good afternoon', 'namaste', 'namaskar']
    if any(g in message_lower for g in greetings):
        resp = "Hello! I'm your **MediSecure AI Insurance Assistant**. I help you understand health insurance premiums, compare plans, and find the best coverage for your needs.\n\n"
        resp += "I can help you with:\n"
        resp += "  **Premium Calculation** - How your premium is calculated\n"
        resp += "  **Plan Comparison** - Compare different insurance companies\n"
        resp += "  **Health Impact** - How your health affects your premium\n"
        resp += "  **Cost Saving Tips** - Ways to reduce your premium\n"
        resp += "  **Policy Terms** - Deductibles, NCB, co-pay, riders explained\n"
        resp += "  **Claim Process** - How to file claims\n\n"
        if has_profile():
            resp += profile_summary() + "\n\n"
            resp += "Ask me anything about your premium or health insurance!"
        else:
            resp += "Fill in your details on the main form to get personalized advice!"
        return resp
    
    if 'who are you' in message_lower or 'what are you' in message_lower or 'your name' in message_lower or 'about you' in message_lower:
        return "I'm the **MediSecure AI Insurance Assistant** - your personal health insurance advisor. I'm built into this premium prediction platform to help you:\n\n" \
               "1. Understand how your health profile affects your insurance premium\n" \
               "2. Compare plans from top Indian insurers (HDFC ERGO, ICICI Lombard, Star Health, etc.)\n" \
               "3. Get tips to reduce your premium\n" \
               "4. Understand insurance terms like NCB, deductible, co-pay, riders\n" \
               "5. Navigate the claim process\n\n" \
               "I'm here to make health insurance simple and transparent. What would you like to know?"
    
    if 'thank' in message_lower or 'thanks' in message_lower:
        return "You're welcome! I'm here to help with any insurance questions. Feel free to ask about premiums, plan comparisons, health impacts, or anything else. Happy to help!"
    
    if 'bye' in message_lower or 'goodbye' in message_lower or 'see you' in message_lower:
        return "Goodbye! Take care of your health, and remember - good health insurance is the best investment you can make. Come back anytime you need insurance advice!"
    
    keywords = []
    topic_map = {
        'premium': ['premium', 'cost', 'price', 'rate', 'charges', 'fees', 'amount'],
        'age': ['age', 'old', 'young', 'years old', 'senior', 'elder'],
        'bmi': ['bmi', 'weight', 'obese', 'obesity', 'overweight', 'underweight'],
        'smoker': ['smoke', 'smoker', 'smoking', 'tobacco', 'cigarette'],
        'children': ['children', 'child', 'kids', 'baby', 'dependent', 'family'],
        'state': ['state', 'city', 'location', 'region', 'metro', 'zone', 'place'],
        'deductible': ['deductible', 'deduct'],
        'ncb': ['ncb', 'no claim', 'no-claim', 'claim bonus'],
        'copay': ['co-pay', 'copay', 'co pay', 'percentage'],
        'rider': ['rider', 'add-on', 'addon', 'extra cover', 'additional'],
        'sum_insured': ['sum insured', 'coverage', 'cover amount', 'how much cover'],
        'claim': ['claim', 'reimbursement', 'cashless', 'hospital bill'],
        'disease': ['disease', 'diabetes', 'heart', 'cancer', 'bp', 'pressure', 'sugar', 'condition', 'illness', 'health issue'],
        'comparison': ['compare', 'vs', 'versus', 'which is better', 'which company', 'best company', 'best plan'],
        'company': ['hdfc', 'icici', 'bajaj', 'star health', 'niva', 'max bupa', 'care', 'reliance', 'manipal', 'national insurance', 'oriental'],
        'maternity': ['maternity', 'pregnant', 'pregnancy', 'delivery', 'childbirth'],
        'tax': ['tax', '80d', 'deduction', 'exemption', 'save tax'],
        'network': ['network', 'hospital', 'cashless hospital', 'nearby hospital'],
        'waiting': ['waiting period', 'waiting', 'when covered', 'how long'],
        'mental': ['mental health', 'depression', 'anxiety', 'stress', 'psychiatric'],
        'recommend': ['recommend', 'suggest', 'which plan', 'which insurance', 'best for me', 'what should i buy'],
        'save': ['save', 'reduce', 'lower', 'decrease', 'cheap', 'affordable', 'discount'],
        'what-if': ['what if', 'what happens if', 'if i', 'suppose'],
    }
    
    for topic, terms in topic_map.items():
        for term in terms:
            if term in message_lower:
                keywords.append(topic)
                break
    
    keywords = list(dict.fromkeys(keywords))
    
    if not keywords:
        return "I'm your MediSecure Insurance Assistant. I specialize in health insurance premium prediction and planning.\n\n" \
               "I didn't quite understand your question, but I can help with:\n\n" \
               "  **Premium factors** - Age, BMI, smoking, location, etc.\n" \
               "  **Plan features** - Deductibles, NCB, co-pay, riders\n" \
               "  **Company comparisons** - HDFC ERGO vs ICICI vs Star Health, etc.\n" \
               "  **Health conditions** - How diseases affect your premium\n" \
               "  **Cost saving** - Ways to reduce your premium\n" \
               "  **Claims** - How to file and what documents you need\n\n" \
               "Try asking something like: *\"How does smoking affect my premium?\"* or *\"Compare HDFC and ICICI\"*"
    
    response_parts = []
    
    if 'premium' in keywords:
        base = "Your insurance premium is calculated based on multiple factors:\n\n"
        base += "**Key Factors:**\n"
        base += "  **Age** - Premiums increase ~8-10% per year after age 30\n"
        base += "  **BMI** - Normal BMI (18.5-24.9) gets best rates; obesity adds 10-30%\n"
        base += "  **Smoking** - Smokers pay 15-25% more due to health risks\n"
        base += "  **Location** - Metro cities (Zone A) cost 25% more than Tier-2 (Zone C)\n"
        base += "  **Sum Insured** - Higher coverage = higher premium\n"
        base += "  **Health Conditions** - Pre-existing diseases add risk loading\n"
        base += "  **Add-ons** - Deductibles reduce premium; riders increase it\n\n"
        if has_profile():
            base += profile_summary() + "\n\n"
            base += "Want to know how to reduce your premium? Ask me about cost saving tips!"
        else:
            base += "Fill in your details on the main form to see your exact premium breakdown!"
        response_parts.append(base)
    
    if 'age' in keywords:
        age_info = "**How Age Affects Your Premium:**\n\n"
        age_info += "Age is the single biggest factor in premium calculation:\n\n"
        age_info += "| Age Group | Premium Impact |\n"
        age_info += "|-----------|----------------|\n"
        age_info += "| 18-25 | Base rate (lowest) |\n"
        age_info += "| 26-35 | +10-15% |\n"
        age_info += "| 36-45 | +25-35% |\n"
        age_info += "| 46-55 | +50-70% |\n"
        age_info += "| 56-65 | +100-150% |\n"
        age_info += "| 65+ | +200%+ (limited plans) |\n\n"
        age_info += "**Why?** Health risks increase with age, so insurers charge more. Buying young locks in lower rates for life."
        if has_profile():
            age_info += "\n\nAt your age ({}), {}.".format(
                profile.get('age'),
                "you're in a good bracket for affordable premiums" if profile.get('age', 0) < 40
                else "premiums are higher but comprehensive coverage is essential"
            )
        response_parts.append(age_info)
    
    if 'bmi' in keywords:
        bmi_info = "**How BMI Affects Your Premium:**\n\n"
        bmi_info += "BMI (Body Mass Index) is a key health indicator insurers use:\n\n"
        bmi_info += "| BMI Range | Category | Premium Impact |\n"
        bmi_info += "|-----------|----------|----------------|\n"
        bmi_info += "| Below 18.5 | Underweight | +5-10% |\n"
        bmi_info += "| 18.5-24.9 | Normal | Best rates |\n"
        bmi_info += "| 25-29.9 | Overweight | +10-20% |\n"
        bmi_info += "| 30-34.9 | Obese Class I | +20-30% |\n"
        bmi_info += "| 35+ | Obese Class II+ | +30-50% |\n\n"
        bmi_info += "**Tip:** Reducing BMI from 30 to 25 can save you Rs.2,000-5,000/year on premiums!"
        if has_profile():
            bmi = profile.get('bmi', 25)
            if bmi > 25:
                bmi_info += "\n\nYour BMI is {}. Getting it to the normal range (18.5-24.9) could significantly lower your premium.".format(bmi)
            else:
                bmi_info += "\n\nYour BMI of {} is in a healthy range - great for premium rates!".format(bmi)
        response_parts.append(bmi_info)
    
    if 'smoker' in keywords:
        smoke_info = "**How Smoking Affects Your Premium:**\n\n"
        smoke_info += "Smoking is one of the biggest premium increase factors:\n\n"
        smoke_info += "  **Smokers pay 15-25% more** than non-smokers\n"
        smoke_info += "  A Rs.30,000 premium becomes Rs.36,000-37,500 for smokers\n\n"
        smoke_info += "**Why?** Smokers have higher risks of:\n"
        smoke_info += "  - Lung cancer (25x higher risk)\n"
        smoke_info += "  - Heart disease (2-4x higher risk)\n"
        smoke_info += "  - Respiratory diseases\n\n"
        smoke_info += "**Good News:** If you quit smoking, many insurers reclassify you as a non-smoker after 12 months of being smoke-free, reducing your premium significantly!"
        if has_profile() and profile.get('smoker','no').lower() == 'yes':
            smoke_info += "\n\nSince you're a smoker, quitting could save you Rs.5,000-10,000/year on premiums!"
        response_parts.append(smoke_info)
    
    if 'deductible' in keywords:
        ded_info = "**Understanding Deductibles:**\n\n"
        ded_info += "A deductible is the amount YOU pay before the insurer covers the rest.\n\n"
        ded_info += "**Example:** With Rs.50,000 deductible and Rs.2,00,000 bill:\n"
        ded_info += "  - You pay: Rs.50,000\n"
        ded_info += "  - Insurer pays: Rs.1,50,000\n\n"
        ded_info += "**Deductible Options & Savings:**\n"
        ded_info += "  - Rs.0 (No deductible) - Highest premium\n"
        ded_info += "  - Rs.25,000 - Save ~8% on premium\n"
        ded_info += "  - Rs.50,000 - Save ~15% on premium\n"
        ded_info += "  - Rs.1,00,000 - Save ~20% on premium\n"
        ded_info += "  - Rs.2,00,000 - Save ~25% on premium\n\n"
        ded_info += "**Smart Strategy:** If you have emergency savings, choose a higher deductible to reduce your annual premium. You save money every year you don't claim."
        response_parts.append(ded_info)
    
    if 'ncb' in keywords:
        ncb_info = "**No Claim Bonus (NCB) Explained:**\n\n"
        ncb_info += "NCB rewards you for every claim-free year:\n\n"
        ncb_info += "| Claim-Free Years | NCB Discount |\n"
        ncb_info += "|-----------------|---------------|\n"
        ncb_info += "| 1 year | 20% |\n"
        ncb_info += "| 2 years | 25% |\n"
        ncb_info += "| 3 years | 33% |\n"
        ncb_info += "| 4 years | 45% |\n"
        ncb_info += "| 5+ years | 50% (maximum) |\n\n"
        ncb_info += "**Pro Tip:** For small claims under Rs.10,000, it's often better to pay out-of-pocket and preserve your NCB. A 50% NCB on a Rs.30,000 premium saves you Rs.15,000/year!"
        response_parts.append(ncb_info)
    
    if 'copay' in keywords:
        copay_info = "**Understanding Co-pay:**\n\n"
        copay_info += "Co-pay is a percentage of EACH claim that you pay yourself.\n\n"
        copay_info += "**Example:** 10% co-pay on Rs.1,00,000 bill:\n"
        copay_info += "  - You pay: Rs.10,000\n"
        copay_info += "  - Insurer pays: Rs.90,000\n\n"
        copay_info += "**Co-pay vs Deductible:**\n"
        copay_info += "  - Deductible: One-time fixed amount per year\n"
        copay_info += "  - Co-pay: Percentage on every claim\n\n"
        copay_info += "**Co-pay Options & Savings:**\n"
        copay_info += "  - 0% - No savings on premium\n"
        copay_info += "  - 10% - Save ~5%\n"
        copay_info += "  - 15% - Save ~8%\n"
        copay_info += "  - 20% - Save ~12%\n"
        copay_info += "  - 25% - Save ~15%\n\n"
        copay_info += "Co-pay is common in senior citizen policies. For younger, healthy individuals, 0% co-pay is usually worth the slightly higher premium."
        response_parts.append(copay_info)
    
    if 'rider' in keywords:
        rider_info = "**Insurance Riders (Add-ons) Explained:**\n\n"
        rider_info += "Riders are optional benefits added to your base policy:\n\n"
        rider_info += "**Available Riders:**\n\n"
        rider_info += "1. **Basic** (Personal Accident Cover)\n"
        rider_info += "   - Accidental death & disability coverage\n"
        rider_info += "   - Cost: ~Rs.1,000-2,000/year\n\n"
        rider_info += "2. **Comprehensive** (Best Value)\n"
        rider_info += "   - Personal accident + Critical illness + Hospital cash\n"
        rider_info += "   - Hospital cash: Rs.500-1,000/day\n"
        rider_info += "   - Cost: ~Rs.3,000-5,000/year\n\n"
        rider_info += "3. **Premium** (Maximum Coverage)\n"
        rider_info += "   - All Comprehensive benefits + Worldwide coverage\n"
        rider_info += "   - Air ambulance, international second opinion\n"
        rider_info += "   - Cost: ~Rs.6,000-10,000/year\n\n"
        rider_info += "**My Recommendation:** Comprehensive rider gives the best value for money."
        response_parts.append(rider_info)
    
    if 'claim' in keywords:
        claim_info = "**Health Insurance Claim Process:**\n\n"
        claim_info += "**Two Types of Claims:**\n\n"
        claim_info += "**1. Cashless Claims (Recommended):**\n"
        claim_info += "   - Use a network hospital (10,000+ across India)\n"
        claim_info += "   - Inform 48 hrs before planned admission (24 hrs for emergency)\n"
        claim_info += "   - Show health card + ID at hospital\n"
        claim_info += "   - Hospital handles paperwork - no upfront payment\n\n"
        claim_info += "**2. Reimbursement Claims:**\n"
        claim_info += "   - Used at non-network hospitals\n"
        claim_info += "   - Pay bills first, submit documents within 15 days\n"
        claim_info += "   - Reimbursement processed within 30 days\n\n"
        claim_info += "**Documents Needed:**\n"
        claim_info += "   - Claim form, hospital bills, discharge summary\n"
        claim_info += "   - Medical reports, policy document, ID proof"
        response_parts.append(claim_info)
    
    if 'disease' in keywords:
        disease_info = "**How Health Conditions Affect Your Premium:**\n\n"
        disease_info += "Pre-existing diseases increase your premium due to higher risk:\n\n"
        disease_info += "| Condition | Premium Impact |\n"
        disease_info += "|-----------|----------------|\n"
        disease_info += "| Diabetes | +15-25% |\n"
        disease_info += "| Hypertension (BP) | +10-20% |\n"
        disease_info += "| Heart Disease | +25-40% |\n"
        disease_info += "| Cancer (history) | +30-50% |\n"
        disease_info += "| Thyroid | +5-10% |\n"
        disease_info += "| Multiple conditions | +30-60% |\n\n"
        disease_info += "**Important:**\n"
        disease_info += "  - Always disclose pre-existing conditions\n"
        disease_info += "  - Non-disclosure can lead to claim rejection\n"
        disease_info += "  - Some plans cover PED from Day 1 (with loading)\n"
        disease_info += "  - PED waiting periods: 2-4 years depending on insurer"
        if has_profile() and profile.get('diseases'):
            disease_info += "\n\nYour conditions ({}) are factored into your premium. ".format(', '.join([d.title() for d in profile['diseases']]))
            disease_info += "Managing these conditions well can help reduce your premium at renewal."
        response_parts.append(disease_info)
    
    if 'comparison' in keywords or 'company' in keywords:
        if 'vs' in message_lower or 'compare' in message_lower or 'versus' in message_lower:
            company_map = {
                'hdfc': 'hdfc_ergo', 'icici': 'icici_lombard', 'bajaj': 'bajaj_allianz',
                'star': 'star_health', 'niva': 'max_bupa', 'max bupa': 'max_bupa',
                'care': 'care_health', 'reliance': 'reliance_general', 'manipal': 'manipalcigna',
                'national': 'national_insurance', 'oriental': 'oriental_insurance',
            }
            companies = []
            for key, cid in company_map.items():
                if key in message_lower and cid not in companies:
                    companies.append(cid)
            if len(companies) >= 2:
                comp_output = "**Company Comparison:**\n\n"
                for cid in companies[:4]:
                    c = INSURANCE_COMPANIES[cid]
                    comp_output += "**{}**\n".format(c['name'])
                    comp_output += "  - CSR: {}\n".format(c['claim_settlement_ratio'])
                    comp_output += "  - Network: {:,} hospitals\n".format(c['network_hospitals'])
                    plans_list = ', '.join([p['name'] for p in c['plans'].values()])
                    comp_output += "  - Plans: {}\n\n".format(plans_list)
                best_csr = max(companies, key=lambda cid: float(INSURANCE_COMPANIES[cid]['claim_settlement_ratio'].replace('%', '')))
                comp_output += "**Verdict:** {} has the highest Claim Settlement Ratio at {}.\n".format(INSURANCE_COMPANIES[best_csr]['name'], INSURANCE_COMPANIES[best_csr]['claim_settlement_ratio'])
                comp_output += "Higher CSR means better claim approval rates."
                response_parts.append(comp_output)
            else:
                comp_output = "**Top Insurance Companies by CSR:**\n\n"
                sorted_companies = sorted(INSURANCE_COMPANIES.items(), key=lambda x: float(x[1]['claim_settlement_ratio'].replace('%', '')), reverse=True)
                for i, (cid, c) in enumerate(sorted_companies[:5], 1):
                    comp_output += "{}. **{}** - CSR: {:,} hospitals\n".format(i, c['name'], c['claim_settlement_ratio'], c['network_hospitals'])
                response_parts.append(comp_output)
        else:
            company_name = None
            company_id = None
            for cid, cdata in INSURANCE_COMPANIES.items():
                if cdata['name'].lower() in message_lower or cid.replace('_', ' ').lower() in message_lower:
                    company_name = cdata['name']
                    company_id = cid
                    break
            if company_id:
                c = INSURANCE_COMPANIES[company_id]
                comp_output = "**{}**\n\n".format(c['name'])
                comp_output += "Claim Settlement Ratio: {}\n".format(c['claim_settlement_ratio'])
                comp_output += "Network Hospitals: {:,}\n".format(c['network_hospitals'])
                comp_output += "Founded: {}\n\n".format(c['founded'])
                comp_output += "**Available Plans:**\n\n"
                for pid, plan in c['plans'].items():
                    comp_output += "- **{}**: {} coverage, from Rs.{:,}/year\n".format(plan['name'], plan['coverage_range'], plan['starting_premium'])
                response_parts.append(comp_output)
            else:
                comp_output = "**Top Insurance Companies:**\n\n"
                sorted_companies = sorted(INSURANCE_COMPANIES.items(), key=lambda x: float(x[1]['claim_settlement_ratio'].replace('%', '')), reverse=True)
                for i, (cid, c) in enumerate(sorted_companies[:5], 1):
                    comp_output += "{}. **{}** - CSR: {:,} hospitals\n".format(i, c['name'], c['claim_settlement_ratio'], c['network_hospitals'])
                comp_output += "\nAsk me to compare specific companies (e.g., 'HDFC vs ICICI') for detailed analysis!"
                response_parts.append(comp_output)
    
    if 'recommend' in keywords:
        if has_profile():
            rec_output = "**Personalized Recommendations:**\n\n"
            rec_output += profile_summary() + "\n\n"
            rec_output += "Based on your profile, here are my suggestions:\n\n"
            if profile.get('smoker','no').lower() == 'yes':
                rec_output += "  - **Critical Illness cover** is essential for smokers\n"
            if profile.get('bmi', 25) > 30:
                rec_output += "  - Consider a plan with **wellness benefits** for weight management\n"
            if profile.get('age', 30) > 50:
                rec_output += "  - Look for plans with **shorter PED waiting periods**\n"
            if profile.get('diseases'):
                rec_output += "  - Your conditions ({}) mean you need comprehensive coverage\n".format(', '.join([d.title() for d in profile['diseases']]))
            if profile.get('children', 0) > 0:
                rec_output += "  - **Family Floater** plan would be cost-effective\n"
            if not profile.get('smoker') and profile.get('bmi', 25) < 25 and profile.get('age', 30) < 40 and not profile.get('diseases'):
                rec_output += "  - You're in a **low-risk category** - great premiums available!\n"
            rec_output += "\nFor exact plan comparisons, try: *'Compare HDFC and ICICI'* or *'Best plan for me'*"
            response_parts.append(rec_output)
        else:
            response_parts.append("I'd love to give personalized recommendations, but I need your profile first! Fill in your details (age, BMI, smoking status, health conditions) on the main form, then ask me again for tailored advice.")
    
    if 'save' in keywords:
        save_info = "**Ways to Reduce Your Insurance Premium:**\n\n"
        save_info += "1. **Quit Smoking** - Save 15-25% (Rs.5,000-10,000/year)\n"
        save_info += "2. **Maintain Healthy BMI** - Save 10-20%\n"
        save_info += "3. **Choose Higher Deductible** - Save up to 25%\n"
        save_info += "4. **Opt for Co-pay** - Save 5-15%\n"
        save_info += "5. **Build No Claim Bonus** - Up to 50% discount over 5 years\n"
        save_info += "6. **Buy Early** - Younger = cheaper premiums\n"
        save_info += "7. **Annual Payment** - Some insurers offer 2-3% discount\n"
        save_info += "8. **Compare Companies** - Premiums vary 20-30% across insurers\n"
        save_info += "9. **Family Floater** - Cheaper than individual plans for families\n"
        save_info += "10. **Tax Benefits** - Save tax under Section 80D (up to Rs.1,00,000)\n\n"
        if has_profile():
            save_info += profile_summary() + "\n\n"
            if profile.get('smoker','no').lower() == 'yes':
                save_info += "**Your biggest saving opportunity:** Quitting smoking could save you Rs.5,000-10,000/year!\n"
            if profile.get('bmi', 25) > 25:
                save_info += "**Your second opportunity:** Reducing BMI to normal range could save Rs.2,000-5,000/year!\n"
        response_parts.append(save_info)
    
    if 'tax' in keywords:
        tax_info = "**Tax Benefits Under Section 80D:**\n\n"
        tax_info += "Health insurance premiums are tax-deductible:\n\n"
        tax_info += "| Coverage For | Deduction Limit |\n"
        tax_info += "|-------------|------------------|\n"
        tax_info += "| Self, Spouse, Children | Rs.25,000/year |\n"
        tax_info += "| Parents (below 60) | Rs.25,000/year |\n"
        tax_info += "| Parents (60+) | Rs.50,000/year |\n"
        tax_info += "| Preventive Check-up | Rs.5,000 (within above) |\n\n"
        tax_info += "**Maximum Deduction: Rs.1,00,000/year**\n\n"
        tax_info += "**Example:** If you're 35 with parents aged 62:\n"
        tax_info += "  - Your family premium: Rs.25,000 - Full deduction\n"
        tax_info += "  - Parents' premium: Rs.45,000 - Rs.50,000 deduction\n"
        tax_info += "  - Total deduction: Rs.75,000\n"
        tax_info += "  - Tax saved (30% slab): Rs.22,500/year"
        response_parts.append(tax_info)
    
    if 'sum_insured' in keywords:
        si_info = "**Choosing the Right Sum Insured:**\n\n"
        si_info += "Sum insured = maximum amount insurer pays per year.\n\n"
        si_info += "| Coverage | Best For |\n"
        si_info += "|----------|----------|\n"
        si_info += "| Rs.5 Lakhs | Young individuals, basic cover |\n"
        si_info += "| Rs.10 Lakhs | Small families, standard cover |\n"
        si_info += "| Rs.15 Lakhs | Families of 3-4 |\n"
        si_info += "| Rs.25 Lakhs | Comprehensive family cover |\n"
        si_info += "| Rs.50 Lakhs | Metro cities, high-risk profiles |\n"
        si_info += "| Rs.1 Crore | Maximum protection |\n\n"
        si_info += "**Rule of Thumb:** Your sum insured should be at least 10x your annual income."
        response_parts.append(si_info)
    
    if 'maternity' in keywords:
        mat_info = "**Maternity Coverage:**\n\n"
        mat_info += "**What's Covered:**\n"
        mat_info += "  - Normal & C-section delivery costs\n"
        mat_info += "  - Pre and post-natal care\n"
        mat_info += "  - Newborn baby cover (usually from Day 1)\n\n"
        mat_info += "**Coverage Amounts:**\n"
        mat_info += "  - Normal Delivery: Rs.15,000-50,000\n"
        mat_info += "  - C-Section: Rs.50,000-1,00,000\n"
        mat_info += "  - Premium plans: Up to Rs.2,00,000\n\n"
        mat_info += "**Important:** Maternity has a 2-4 year waiting period. Buy a policy NOW if you're planning a family in 2-3 years!"
        response_parts.append(mat_info)
    
    if 'network' in keywords:
        net_info = "**Network Hospitals (Cashless Treatment):**\n\n"
        net_info += "**Why it matters:** Network hospitals offer zero upfront payment and hassle-free claims.\n\n"
        net_info += "**Network Sizes:**\n"
        net_info += "  - Star Health: 14,000+ hospitals (largest)\n"
        net_info += "  - HDFC ERGO: 12,500+ hospitals\n"
        net_info += "  - Care Health: 11,000+ hospitals\n"
        net_info += "  - Niva Bupa: 10,000+ hospitals\n"
        net_info += "  - ICICI Lombard: 8,000+ hospitals\n"
        net_info += "  - ManipalCigna: 8,500+ hospitals\n"
        net_info += "  - Bajaj Allianz: 7,000+ hospitals\n\n"
        net_info += "**Tip:** Before buying, check if hospitals near your home/work are in the network."
        response_parts.append(net_info)
    
    if 'waiting' in keywords:
        wait_info = "**Understanding Waiting Periods:**\n\n"
        wait_info += "Waiting periods are the time before certain benefits activate:\n\n"
        wait_info += "| Type | Duration |\n"
        wait_info += "|------|----------|\n"
        wait_info += "| Initial (general illness) | 30 days |\n"
        wait_info += "| Accidents | Day 1 |\n"
        wait_info += "| Pre-existing Diseases | 2-4 years |\n"
        wait_info += "| Specific Procedures | 1-2 years |\n"
        wait_info += "| Maternity | 2-4 years |\n\n"
        wait_info += "**Key Point:** Buy early - every day you wait adds to your waiting period. Some insurers offer reduced waiting periods for extra premium."
        response_parts.append(wait_info)
    
    if 'mental' in keywords:
        mental_info = "**Mental Health Coverage:**\n\n"
        mental_info += "Mental health coverage is now mandatory in all Indian health insurance policies.\n\n"
        mental_info += "**What's Covered:**\n"
        mental_info += "  - Inpatient hospitalization for psychiatric conditions\n"
        mental_info += "  - Psychiatrist & psychologist consultations\n"
        mental_info += "  - Therapy and counseling (premium plans)\n"
        mental_info += "  - Treatment for depression, anxiety, bipolar disorder\n\n"
        mental_info += "**Note:** Standard waiting period is 30 days for new conditions. Pre-existing mental health conditions: 2-4 years waiting period."
        response_parts.append(mental_info)
    
    if 'children' in keywords:
        child_info = "**Health Insurance with Dependents:**\n\n"
        child_info += "Having children/dependents affects your insurance needs:\n\n"
        child_info += "**Recommendations:**\n"
        child_info += "  - **Family Floater** plans are most cost-effective\n"
        child_info += "  - Sum insured should be higher (shared across family)\n"
        child_info += "  - Add newborn within 90 days of birth\n"
        child_info += "  - Children covered until age 25 (if dependent)\n\n"
        child_info += "**Coverage Suggestions:**\n"
        child_info += "  - Family of 3: Rs.10-15 Lakhs\n"
        child_info += "  - Family of 4: Rs.15-25 Lakhs\n"
        child_info += "  - Family with parents: Rs.25-50 Lakhs"
        response_parts.append(child_info)
    
    if 'state' in keywords:
        state_info = "**How Location Affects Your Premium:**\n\n"
        state_info += "Healthcare costs vary significantly across India:\n\n"
        state_info += "| Zone | Cities | Premium Factor |\n"
        state_info += "|------|--------|----------------|\n"
        state_info += "| Zone A (Metro) | Delhi, Mumbai, Bangalore, Chennai | 1.25x |\n"
        state_info += "| Zone B (Tier-1) | Pune, Ahmedabad, Hyderabad | 1.00x |\n"
        state_info += "| Zone C (Tier-2/3) | Jaipur, Lucknow, Rural areas | 0.88x |\n\n"
        state_info += "**Why?** Metro cities have higher hospital costs, more pollution, and lifestyle-related health risks."
        if has_profile():
            state_info += "\n\nYour state ({}) falls under Zone {}. ".format(profile.get('state','?').title(), 'A' if profile.get('state','').lower() in ['delhi','maharashtra','karnataka','tamil nadu'] else 'B')
            state_info += "Moving to a lower zone could reduce your premium by 12-25%."
        response_parts.append(state_info)
    
    if 'what-if' in keywords:
        whatif_info = "**What-If Scenario Planning:**\n\n"
        whatif_info += "Here's how common changes affect your premium:\n\n"
        whatif_info += "| Change | Premium Impact |\n"
        whatif_info += "|--------|----------------|\n"
        whatif_info += "| Quit smoking | -15-25% |\n"
        whatif_info += "| BMI 30 to 25 | -10-20% |\n"
        whatif_info += "| Add Rs.50K deductible | -15% |\n"
        whatif_info += "| 20% Co-pay | -10% |\n"
        whatif_info += "| 50% NCB (after 5 years) | -50% |\n"
        whatif_info += "| Increase sum insured 10L to 25L | +40-60% |\n"
        whatif_info += "| Add comprehensive rider | +8-12% |\n\n"
        whatif_info += "Use the **What-If Simulator** on the main page to test different scenarios in real-time!"
        response_parts.append(whatif_info)
    
    if not response_parts:
        return "I understand you're asking about insurance, but I need a bit more context. Try asking:\n\n" \
               "  *\"How is premium calculated?\"*\n" \
               "  *\"How does BMI affect my premium?\"*\n" \
               "  *\"Compare HDFC vs ICICI\"*\n" \
               "  *\"Ways to reduce my premium\"*\n" \
               "  *\"What is NCB?\"*\n\n" \
               "I'm here to help with any health insurance question!"
    
    return "\n\n---\n\n".join(response_parts)

def generate_company_info(company_id):
    company = INSURANCE_COMPANIES.get(company_id)
    if not company:
        return "Company not found. Try HDFC ERGO, ICICI Lombard, Bajaj Allianz, Star Health, Niva Bupa, or Care Health."
    
    plans = company['plans']
    output = f"**{company['name']}**\n\n"
    output += f"Claim Settlement Ratio: {company['claim_settlement_ratio']}\n"
    output += f"Network Hospitals: {company['network_hospitals']:,}\n"
    output += f"Founded: {company['founded']}\n\n"
    output += "**Available Plans:**\n\n"
    for pid, plan in plans.items():
        output += f"**{plan['name']}**\n"
        output += f"- Coverage: {plan['coverage_range']}\n"
        output += f"- Starting Premium: Rs.{plan['starting_premium']:,}/year\n"
        output += f"- PED Waiting: {plan['waiting_period_ped']}\n"
        output += f"- Features: {', '.join(plan['features'][:3])}\n\n"
    return output

def generate_vs_comparison(message_lower):
    company_map = {
        'hdfc': 'hdfc_ergo', 'icici': 'icici_lombard', 'bajaj': 'bajaj_allianz',
        'star': 'star_health', 'niva': 'max_bupa', 'max bupa': 'max_bupa',
        'care': 'care_health', 'reliance': 'reliance_general', 'manipal': 'manipalcigna',
        'national': 'national_insurance', 'oriental': 'oriental_insurance',
    }
    companies = []
    for key, cid in company_map.items():
        if key in message_lower:
            if cid not in companies:
                companies.append(cid)
    
    if len(companies) < 2:
        return "Please mention at least 2 companies to compare. For example: HDFC vs ICICI"
    
    output = "**Company Comparison:**\n\n"
    for cid in companies[:4]:
        c = INSURANCE_COMPANIES[cid]
        output += f"**{c['name']}**\n"
        output += f"- CSR: {c['claim_settlement_ratio']}\n"
        output += f"- Network: {c['network_hospitals']:,} hospitals\n"
        output += f"- Founded: {c['founded']}\n"
        plans_list = ', '.join([p['name'] for p in c['plans'].values()])
        output += f"- Plans: {plans_list}\n\n"
    
    best_csr = max(companies, key=lambda cid: float(INSURANCE_COMPANIES[cid]['claim_settlement_ratio'].replace('%', '')))
    best_network = max(companies, key=lambda cid: INSURANCE_COMPANIES[cid]['network_hospitals'])
    
    output += f"**Verdict:**\n"
    output += f"• Highest Claim Settlement: {INSURANCE_COMPANIES[best_csr]['name']} ({INSURANCE_COMPANIES[best_csr]['claim_settlement_ratio']})\n"
    output += f"• Largest Network: {INSURANCE_COMPANIES[best_network]['name']} ({INSURANCE_COMPANIES[best_network]['network_hospitals']:,} hospitals)\n\n"
    output += "Fill in your profile for personalized recommendations based on your health needs."
    return output

def generate_company_comparison(profile: Dict) -> str:
    age = profile.get('age', 30)
    state = profile.get('state', 'Unknown')
    diseases = profile.get('diseases', [])
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    bmi = profile.get('bmi', 25)
    children = profile.get('children', 0)
    predicted_cost = profile.get('predicted_cost', 0)
    
    criteria = {
        'has_diabetes': any('diabet' in d.lower() for d in diseases),
        'has_heart_disease': any('heart' in d.lower() for d in diseases),
        'needs_senior': age > 60,
        'needs_critical_illness': smoker or len(diseases) > 0,
        'coverage_type': 'family' if children > 0 or age > 35 else 'individual',
    }
    
    if age < 35 and len(diseases) == 0:
        criteria['budget'] = 'low'
    elif age < 50 and len(diseases) <= 1:
        criteria['budget'] = 'medium'
    else:
        criteria['budget'] = 'high'
    
    if any('maternity' in d.lower() for d in diseases):
        criteria['needs_maternity'] = True
    
    recommended_plans = filter_plans(criteria)
    
    output = "## Company & Plan Comparison\n\n"
    output += f"**Based on your profile:** Age {age}, {state.title()}, "
    if diseases:
        output += f"Health: {', '.join([d.title() for d in diseases])}"
    if smoker:
        output += ", Smoker"
    output += "\n\n"
    
    if predicted_cost:
        output += f"**Your estimated premium:** Rs.{predicted_cost:,.2f}/year\n\n"
    
    output += "---\n\n"
    output += "### Top Recommendations:\n\n"
    
    for i, plan in enumerate(recommended_plans[:4], 1):
        company = INSURANCE_COMPANIES[plan['company_id']]
        output += f"**{i}. {company['name']}**\n"
        output += f"   **Plan:** {plan['plan_name']}\n"
        output += f"   **Coverage:** {plan['coverage_range']}\n"
        output += f"   **Starting Premium:** Rs.{plan['starting_premium']:,}/year\n"
        output += f"   **Claim Settlement:** {company['claim_settlement_ratio']}\n"
        output += f"   **Network Hospitals:** {company['network_hospitals']:,}\n"
        output += f"   **PED Waiting:** {plan['waiting_period_ped']}\n"
        output += f"   **Key Features:** {', '.join(plan['features'][:3])}\n"
        if plan['reasons']:
            output += f"   **Why this plan:** {', '.join(plan['reasons'][:2])}\n"
        output += "\n"
    
    output += "---\n\n"
    
    if recommended_plans:
        best = recommended_plans[0]
        best_company = INSURANCE_COMPANIES[best['company_id']]
        output += f"**My Top Pick:** {best_company['name']} - {best['plan_name']}\n\n"
        output += f"This plan offers the best combination of claim settlement ratio ({best_company['claim_settlement_ratio']}), "
        output += f"network hospitals ({best_company['network_hospitals']:,}), "
        output += f"and features suited to your profile.\n\n"
    
    output += "Want more details on any of these plans? Ask me to compare specific companies or explain any plan in detail."
    
    return output

def generate_insurance_suggestion(profile: Dict) -> str:
    return generate_company_comparison(profile)
    recommendations = recommend_insurance(profile)
    
    age = profile.get('age', 30)
    state = profile.get('state', 'Unknown')
    diseases = profile.get('diseases', [])
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    bmi = profile.get('bmi', 25)
    predicted_cost = profile.get('predicted_cost', 0)
    
    suggestion = "## Personalized Insurance Recommendation\n\n"
    suggestion += "Based on my analysis of your profile, here are my recommendations:\n\n"
    suggestion += f"**Profile Summary:**\n"
    suggestion += f"- Age: {age} years\n"
    suggestion += f"- Location: {state.title() if state else 'Unknown'}\n"
    suggestion += f"- Health Conditions: {', '.join([d.title() for d in diseases]) if diseases else 'None reported'}\n"
    suggestion += f"- Smoker: {'Yes' if smoker else 'No'}\n"
    suggestion += f"- BMI: {bmi}\n"
    if predicted_cost:
        suggestion += f"- Estimated Annual Premium: Rs.{predicted_cost:,.2f}\n"
    suggestion += "\n"
    
    suggestion += "---\n\n"
    suggestion += "### Recommended Plans:\n\n"
    
    for i, plan in enumerate(recommendations, 1):
        suggestion += f"**{i}. {plan['name']}**\n"
        suggestion += f"   - Coverage: {plan['coverage']}\n"
        suggestion += f"   - Premium Range: {plan['premium_range']}\n"
        suggestion += f"   - Ideal For: {', '.join(plan['best_for'])}\n"
        suggestion += f"   - Key Benefits: {', '.join(plan['features'][:3])}\n\n"
    
    suggestion += "---\n\n"
    
    if smoker or len(diseases) > 0:
        suggestion += "**Recommendation:** Given your health profile, I recommend Option 1. "
        suggestion += "The comprehensive coverage will protect you against complications and provide financial security. "
        suggestion += "The higher premium is justified by the extensive protection it offers.\n\n"
    elif age > 50:
        suggestion += "**Recommendation:** Based on your age, I recommend Option 1 for robust coverage. "
        suggestion += "Health risks increase with age, and adequate coverage now will prevent financial stress later.\n\n"
    else:
        suggestion += "**Recommendation:** Option 1 offers the best value for your profile. "
        suggestion += "Starting with good coverage early means lower premiums and longer protection. "
        suggestion += "Pre-existing conditions that develop after coverage will be included.\n\n"
    
    suggestion += "Feel free to ask any questions about these plans. I'm here to help you choose the right coverage."
    
    return suggestion

def generate_session_id() -> str:
    return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12]

init_db()
configure_gemini()
