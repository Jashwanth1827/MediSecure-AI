import os
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

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

def get_chat_history(session_id: str, limit: int = 20) -> List[Dict]:
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("""SELECT role, message, timestamp FROM chat_messages 
                 WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?""",
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
- Predicted Insurance Cost: ₹{profile.get('predicted_cost', 0):,.2f}
"""

    return f"""You are MediBot, an AI assistant for MediSecure Health Insurance. You help users with:
1. Questions about health and medical conditions
2. Understanding health insurance policies
3. Recommending the best insurance plans based on their profile
4. Explaining medical terms and procedures
5. Providing health tips and preventive care advice

Guidelines:
- Be friendly, helpful, and empathetic
- Provide accurate health information but recommend consulting doctors for specific medical advice
- Always consider the user's profile when recommending insurance
- Explain insurance terms in simple language
- Never make definitive medical diagnoses
- Recommend seeing a healthcare professional for serious concerns

Available Insurance Plans:
- Basic Health Insurance (₹3-5 Lakhs coverage)
- Standard Health Insurance (₹5-10 Lakhs coverage)
- Premium Health Insurance (₹10-25 Lakhs coverage)
- Critical Illness Insurance (₹25 Lakhs-1 Crore lump sum)
- Family Floater Health Insurance (₹5-50 Lakhs shared)
- Senior Citizen Health Insurance (₹3-10 Lakhs)
- Top-Up Health Insurance (₹10-50 Lakhs above deductible)

{profile_context}

Always be concise but thorough. Use bullet points when listing information.
Format your responses nicely with headers and sections where appropriate."""

def chat_with_gemini(message: str, session_id: str) -> str:
    if not GEMINI_CONFIGURED or GEMINI_CLIENT is None:
        return get_local_response(message, session_id)
    
    try:
        profile = get_user_profile(session_id)
        
        full_message = f"{get_system_prompt(profile)}\n\nUser: {message}"
        
        response = GEMINI_CLIENT.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_message,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )
        
        return response.text
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return get_local_response(message, session_id)

def get_local_response(message: str, session_id: str) -> str:
    profile = get_user_profile(session_id)
    message_lower = message.lower()
    
    greetings = ['hi', 'hello', 'hey', 'how are you', 'good morning', 'good evening']
    if any(g in message_lower for g in greetings):
        return f"Hello! 👋 I'm MediBot, your health insurance assistant. I can help you with:\n\n• Understanding insurance policies\n• Choosing the right health plan\n• Answering health-related questions\n• Providing personalized recommendations\n\nWhat would you like to know?"
    
    if 'recommend' in message_lower or 'which insurance' in message_lower or 'best plan' in message_lower:
        if profile:
            return generate_insurance_suggestion(profile)
        return "I'd be happy to recommend an insurance plan! Could you first fill in your details on the main form so I can provide personalized suggestions? Or tell me about your age, health conditions, and budget."
    
    if 'cost' in message_lower or 'price' in message_lower or 'premium' in message_lower:
        return """**Understanding Insurance Costs:**

The cost of health insurance depends on:
• **Age** - Older individuals pay higher premiums
• **Coverage Amount** - Higher coverage = higher premium
• **Health Conditions** - Pre-existing diseases may increase cost
• **Family Size** - Family floater plans cost more
• **Location** - Metro cities have higher premiums

**Typical Premium Ranges (India):**
• Basic: ₹5,000-15,000/year
• Standard: ₹15,000-30,000/year
• Premium: ₹30,000-60,000/year
• Critical Illness: ₹10,000-50,000/year

Would you like me to suggest a plan based on your profile?"""
    
    if 'diabetes' in message_lower or 'sugar' in message_lower:
        return """**Diabetes & Health Insurance:**

If you have diabetes, consider these plans:
• **Premium Health Insurance** - Best for managing diabetes-related complications
• **Critical Illness Insurance** - Provides lump sum for diabetes-related critical conditions
• **Senior Citizen Plan** - If you're 60+, look for plans covering diabetes

**Tips:**
• Look for plans with short pre-existing disease waiting periods
• Compare plans with and without diabetic-specific add-ons
• Some insurers offer wellness programs for diabetics
• Consider a top-up plan to increase coverage

Would you like a personalized recommendation?"""
    
    if 'claim' in message_lower:
        return """**Health Insurance Claim Process:**

**Types of Claims:**
1. **Cashless Claims** - Direct settlement at network hospitals
2. **Reimbursement Claims** - Pay first, claim later

**Steps for Cashless Claim:**
1. Notify insurer 48 hours before hospitalization
2. Carry health card and ID proof
3. Fill pre-authorization form at hospital
4. Insurer settles bill directly with hospital

**Documents Required:**
• Claim form
• Medical reports
• Hospital bills
• Discharge summary
• Policy copy

**Tips:**
• Use network hospitals for cashless claims
• Keep all receipts and documents
• Know your policy's sub-limits and exclusions

Any specific questions about claims?"""
    
    if 'waiting period' in message_lower:
        return """**Understanding Waiting Periods:**

**What is a Waiting Period?**
Time you must wait before certain benefits become active.

**Typical Waiting Periods:**
• General Illnesses: 30 days
• Pre-existing Diseases (PED): 2-4 years
• Specific Diseases: 1-2 years (varies by insurer)
• Maternity: 2-4 years
• COVID-19: 15 days

**Key Points:**
• Emergencies are covered immediately
• You can reduce PED waiting by paying extra premium
• Some insurers offer "No Waiting Period" plans at higher cost

Would you like to know more about specific waiting periods?"""
    
    if 'maternity' in message_lower or 'pregnant' in message_lower:
        return """**Maternity Health Insurance:**

**Key Points:**
• Most plans have 2-4 year waiting period for maternity
• Coverage includes delivery costs (normal & C-section)
• Newborn baby coverage is included in some plans
• Usually covered: ₹15,000-50,000 for normal, ₹50,000-1,00,000 for C-section

**Tips:**
• Buy before planning pregnancy for full benefits
• Look for plans covering:
  - Pre & Post natal care
  - Delivery costs
  - Newborn baby coverage
  - Complication coverage

**Family Floater Plans** often work best for maternity coverage.

Would you like maternity-specific recommendations?"""
    
    if 'mental' in message_lower or 'depression' in message_lower or 'anxiety' in message_lower:
        return """**Mental Health Coverage:**

Great news! Mental health is now covered under health insurance in India (since 2019).

**What's Covered:**
• Inpatient hospitalization for mental illness
• Outpatient treatment (in some premium plans)
• Therapy and counseling (select plans)
• Psychiatric consultations

**Key Points:**
• Standard Waiting Period: 30 days
• Pre-existing mental health conditions: 2-4 years waiting
• Coverage amount varies by plan

**Recommended Plans:**
• Standard or Premium Health Insurance
• Plans with mental wellness programs

Remember: Mental health is as important as physical health. Would you like more information?"""
    
    if 'tax' in message_lower or 'deduction' in message_lower or '80d' in message_lower:
        return """**Tax Benefits under Section 80D:**

**Tax Deductions on Health Insurance Premiums:**

| Category | Deduction Limit |
|----------|----------------|
| Self/Spouse/Children | ₹25,000/year |
| Senior Citizen (60+) | ₹50,000/year |
| Parents (below 60) | ₹25,000/year |
| Parents (60+) | ₹50,000/year |
| Preventive Health Checkup | +₹5,000/year |

**Example:**
If you're 35 with senior citizen parents:
• Your health premium: ₹25,000
• Parents' premium: ₹50,000
• **Total Deduction: ₹75,000**

**Additional Benefits:**
• Preventive health checkup costs also qualify
• Ayurvedic/Homeopathy treatments covered under some plans

Would you like to optimize your tax savings with insurance?"""
    
    if 'network' in message_lower or 'hospital' in message_lower:
        return """**Network Hospitals:**

**What are Network Hospitals?**
Hospitals with cashless facility - insurer pays directly.

**Benefits:**
• No upfront payment required
• Hassle-free claims
• Wide coverage across India

**Tips:**
• Check insurer's network hospital list before buying
• Look for hospitals near your home/work
• Premium plans often have more network hospitals
• Multi-specialty hospitals usually in network

**Top Insurers Network Size:**
• HDFC ERGO: 10,000+ hospitals
• ICICI Lombard: 6,500+ hospitals
• Bajaj Allianz: 6,000+ hospitals
• Star Health: 8,000+ hospitals

Any specific hospital queries?"""
    
    if profile and ('my' in message_lower and ('profile' in message_lower or 'plan' in message_lower or 'recommend' in message_lower)):
        return generate_insurance_suggestion(profile)
    
    return """I'd be happy to help! Here are some topics I can assist with:

**Insurance Questions:**
• Which insurance plan is best for me?
• How much does health insurance cost?
• What does my policy cover?
• How to file a claim?
• Understanding waiting periods

**Health Questions:**
• Managing diabetes/hypertension
• Health tips and preventive care
• Understanding medical terms

**Financial Questions:**
• Tax benefits under 80D
• Claim process and documentation
• Network hospitals

Just ask me anything, or fill in your details on the main form for personalized recommendations! 😊"""

def generate_insurance_suggestion(profile: Dict) -> str:
    recommendations = recommend_insurance(profile)
    
    age = profile.get('age', 30)
    state = profile.get('state', 'Unknown')
    diseases = profile.get('diseases', [])
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    bmi = profile.get('bmi', 25)
    
    suggestion = "## 🏥 Your Personalized Insurance Recommendation\n\n"
    suggestion += f"Based on your profile:\n"
    suggestion += f"- **Age:** {age} years\n"
    suggestion += f"- **Location:** {state.title() if state else 'Unknown'}\n"
    suggestion += f"- **Health Conditions:** {', '.join([d.title() for d in diseases]) if diseases else 'None reported'}\n"
    suggestion += f"- **Smoker:** {'Yes ⚠️' if smoker else 'No'}\n"
    suggestion += f"- **BMI:** {bmi}\n\n"
    
    suggestion += "---\n\n"
    suggestion += "### Recommended Plans:\n\n"
    
    for i, plan in enumerate(recommendations, 1):
        suggestion += f"**{i}. {plan['name']}**\n"
        suggestion += f"   - 💰 Coverage: {plan['coverage']}\n"
        suggestion += f"   - 📊 Premium: {plan['premium_range']}\n"
        suggestion += f"   - 👥 Best For: {', '.join(plan['best_for'])}\n"
        suggestion += f"   - ✨ Key Features: {', '.join(plan['features'][:3])}\n\n"
    
    suggestion += "---\n\n"
    suggestion += "💡 **Tip:** Based on your profile, I'd recommend #{num} for the best coverage.\n\n".format(
        num=1 if smoker or len(diseases) > 0 else (2 if age > 50 else 1)
    )
    
    return suggestion

def generate_session_id() -> str:
    return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12]

init_db()
configure_gemini()
