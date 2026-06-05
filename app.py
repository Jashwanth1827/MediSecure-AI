from flask import Flask, request, render_template, jsonify, session
from werkzeug.utils import secure_filename
import os
import tempfile

from src.mlproject.pipelines.prediction_pipeline import (
    CustomData, PredictPipeline, calculate_final_premium, 
    get_coverage_details, get_sum_insured_display, get_term_display,
    SUM_INSURED_FACTORS, POLICY_TERM_FACTORS, ROOM_TYPE_FACTORS,
    DEDUCTIBLE_FACTORS, COPAY_FACTORS, NCB_FACTORS, RIDER_FACTORS,
    RIDER_BENEFITS, STATE_ZONES, ZONE_MULTIPLIERS
)
from src.mlproject.medical_report_processor import (
    process_medical_report, INDIAN_STATES_COST_FACTOR
)
from src.mlproject.gemini_chatbot import (
    chat_with_gemini, 
    save_message, 
    save_user_profile, 
    get_chat_history, 
    generate_session_id, 
    GEMINI_CONFIGURED,
    update_gemini_key,
    get_user_profile
)
from src.mlproject.health_risk_predictor import (
    calculate_premium_savings,
    generate_prevention_plan,
    calculate_health_score,
    get_ai_insights,
    predict_health_risks
)

# =====================================================================
# ARCHITECTURE ROLE: CONTROLLER & ORCHESTRATOR (MVC - Controller)
# =====================================================================
# This file is the entry point of the Flask application. It defines
# all API and web routes, manages sessions, parses requests, and delegates 
# the heavy lifting (ML predictions, PDF parsing, diagnostic analysis, and 
# chatbot execution) to dedicated modules under `src/mlproject/`.
# It keeps the web routing logic clean and decoupled from business rules.
# =====================================================================

application = Flask(__name__)
app = application
app.secret_key = os.environ.get('SECRET_KEY', 'medisecure-secret-key-12345')

UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

INDIAN_STATES = sorted(INDIAN_STATES_COST_FACTOR.keys())

SUM_INSURED_OPTIONS = [
    ('5_lakhs', '5 Lakhs'),
    ('10_lakhs', '10 Lakhs'),
    ('15_lakhs', '15 Lakhs'),
    ('25_lakhs', '25 Lakhs'),
    ('50_lakhs', '50 Lakhs'),
    ('1_crore', '1 Crore'),
]

POLICY_TERM_OPTIONS = [
    ('1_year', '1 Year'),
    ('2_year', '2 Years'),
    ('3_year', '3 Years'),
]

ROOM_TYPE_OPTIONS = [
    ('general', 'General Ward'),
    ('semi_private', 'Semi-Private'),
    ('private', 'Private Room'),
]

DEDUCTIBLE_OPTIONS = [
    ('0', 'No Deductible'),
    ('25000', 'Rs. 25,000'),
    ('50000', 'Rs. 50,000'),
    ('100000', 'Rs. 1,00,000'),
    ('200000', 'Rs. 2,00,000'),
]

COPAY_OPTIONS = [
    ('0', 'No Co-pay'),
    ('10', '10% Co-pay'),
    ('15', '15% Co-pay'),
    ('20', '20% Co-pay'),
    ('25', '25% Co-pay'),
]

NCB_OPTIONS = [
    ('0', 'No NCB'),
    ('20', '20% NCB'),
    ('25', '25% NCB'),
    ('33', '33% NCB'),
    ('45', '45% NCB'),
    ('50', '50% NCB'),
]

RIDER_OPTIONS = [
    ('none', 'No Riders'),
    ('basic', 'Basic (Personal Accident)'),
    ('comprehensive', 'Comprehensive (PA + CI + Hospital Cash)'),
    ('premium', 'Premium (All Benefits + Worldwide)'),
]

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()
    return session['session_id']

@app.route('/', methods=['GET', 'POST'])
def predict_datapoint():
    if request.method == 'GET':
        session_id = get_session_id()
        return render_template('index.html', 
                             states=INDIAN_STATES, 
                             results=None,
                             session_id=session_id,
                             gemini_configured=GEMINI_CONFIGURED,
                             sum_insured_options=SUM_INSURED_OPTIONS,
                             policy_term_options=POLICY_TERM_OPTIONS,
                             room_type_options=ROOM_TYPE_OPTIONS,
                             deductible_options=DEDUCTIBLE_OPTIONS,
                             copay_options=COPAY_OPTIONS,
                             ncb_options=NCB_OPTIONS,
                             rider_options=RIDER_OPTIONS)
    
    else:
        disease_cost = 0
        disease_details = []
        diseases_found = []
        severity = 'none'
        lab_findings = {}
        report_summary = ''
        session_id = get_session_id()
        
        pdf_file = request.files.get('medical_report')
        
        if pdf_file and pdf_file.filename != '':
            if allowed_file(pdf_file.filename):
                filename = secure_filename(pdf_file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                pdf_file.save(filepath)
                
                report_result = process_medical_report(filepath)
                disease_cost = report_result['additional_cost']
                disease_details = report_result['disease_details']
                diseases_found = report_result['diseases']
                severity = report_result['severity']
                lab_findings = report_result.get('lab_findings', {})
                report_summary = report_result.get('report_summary', '')
                
                os.remove(filepath)
        
        age = float(request.form.get('age', 30))
        sex = request.form.get('sex', 'male')
        bmi = float(request.form.get('bmi', 25))
        children = int(request.form.get('children', 0))
        smoker = request.form.get('smoker', 'no')
        state = request.form.get('state', 'maharashtra')
        
        sum_insured = request.form.get('sum_insured', '10_lakhs')
        policy_term = request.form.get('policy_term', '1_year')
        room_type = request.form.get('room_type', 'general')
        deductible = request.form.get('deductible', '0')
        copay = request.form.get('copay', '0')
        ncb = request.form.get('ncb', '0')
        riders = request.form.get('riders', 'none')
        
        data = CustomData(
            age=age,
            sex=sex,
            bmi=bmi,
            children=children,
            smoker=smoker,
            state=state,
            sum_insured=sum_insured,
            policy_term=policy_term,
            room_type=room_type,
            deductible=deductible,
            copay=copay,
            ncb=ncb,
            riders=riders,
            disease_cost=disease_cost,
            disease_count=len(diseases_found),
            severity=severity
        )
        
        modifiers = data.calculate_premium_modifiers()
        pred_df = data.get_data_as_data_frame()

        predict_pipeline = PredictPipeline()
        base_prediction = predict_pipeline.predict(pred_df)
        
        final_prediction = calculate_final_premium(base_prediction[0], modifiers, disease_cost)
        
        zone = STATE_ZONES.get(state.lower(), 'B')
        
        coverage = get_coverage_details(sum_insured, riders)
        
        health_profile = {
            'age': age,
            'sex': sex,
            'bmi': bmi,
            'children': children,
            'smoker': smoker,
            'state': state
        }
        
        premium_savings = calculate_premium_savings(health_profile, diseases_found, severity)
        prevention_plan = generate_prevention_plan(health_profile, diseases_found, severity)
        health_score = calculate_health_score(health_profile, diseases_found, severity)
        ai_insights = get_ai_insights(health_profile, diseases_found, severity)
        health_risks = predict_health_risks(health_profile, diseases_found, severity)
        
        profile = {
            'age': age,
            'sex': sex,
            'bmi': bmi,
            'children': children,
            'smoker': smoker,
            'state': state,
            'sum_insured': sum_insured,
            'policy_term': policy_term,
            'room_type': room_type,
            'deductible': deductible,
            'copay': copay,
            'ncb': ncb,
            'riders': riders,
            'diseases': diseases_found,
            'severity': severity,
            'predicted_cost': final_prediction
        }
        save_user_profile(session_id, profile)

        return render_template('index.html', 
                             states=INDIAN_STATES,
                             results="{:.2f}".format(final_prediction),
                             base_cost="{:.2f}".format(base_prediction[0]),
                             modifiers=modifiers,
                             disease_cost="{:.2f}".format(disease_cost),
                             diseases_found=diseases_found,
                             severity=severity,
                             disease_details=disease_details,
                             lab_findings=lab_findings,
                             report_summary=report_summary,
                             coverage=coverage,
                             age=age, 
                             sex=sex, 
                             bmi=bmi, 
                             children=children, 
                             smoker=smoker, 
                             state=state,
                             sum_insured=sum_insured,
                             policy_term=policy_term,
                             room_type=room_type,
                             deductible=deductible,
                             copay=copay,
                             ncb=ncb,
                             riders=riders,
                             zone=zone,
                             session_id=session_id,
                             gemini_configured=GEMINI_CONFIGURED,
                             sum_insured_options=SUM_INSURED_OPTIONS,
                             policy_term_options=POLICY_TERM_OPTIONS,
                             room_type_options=ROOM_TYPE_OPTIONS,
                             deductible_options=DEDUCTIBLE_OPTIONS,
                             copay_options=COPAY_OPTIONS,
                             ncb_options=NCB_OPTIONS,
                             rider_options=RIDER_OPTIONS,
                              premium_savings=premium_savings,
                              prevention_plan=prevention_plan,
                              health_score=health_score,
                              ai_insights=ai_insights,
                              health_risks=health_risks)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').strip()
    session_id = get_session_id()
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    save_message(session_id, 'user', message)
    response = chat_with_gemini(message, session_id)
    save_message(session_id, 'assistant', response)
    
    return jsonify({'response': response})

@app.route('/chat/history', methods=['GET'])
def chat_history():
    session_id = get_session_id()
    history = get_chat_history(session_id, limit=50)
    return jsonify({'history': history})

@app.route('/chat/clear', methods=['POST'])
def clear_chat():
    session_id = get_session_id()
    save_message(session_id, 'system', 'Chat cleared')
    return jsonify({'success': True})

@app.route('/api/profile', methods=['GET'])
def api_profile():
    session_id = get_session_id()
    profile = get_user_profile(session_id)
    return jsonify({'profile': profile})

@app.route('/api/premium-calculator')
def premium_calculator():
    age = int(request.args.get('age', 30))
    bmi = float(request.args.get('bmi', 25))
    sum_insured = request.args.get('sum_insured', '10_lakhs')
    policy_term = request.args.get('policy_term', '1_year')
    
    data = CustomData(
        age=age, sex='male', bmi=bmi, children=0,
        smoker='no', state='maharashtra',
        sum_insured=sum_insured, policy_term=policy_term
    )
    modifiers = data.calculate_premium_modifiers()
    
    return jsonify({
        'factors': modifiers,
        'sum_insured_display': get_sum_insured_display(sum_insured),
        'term_display': get_term_display(policy_term)
    })

@app.route('/api/compare-plans', methods=['POST'])
def api_compare_plans():
    data = request.get_json(silent=True) or {}
    criteria = {
        'budget': data.get('budget', 'medium'),
        'coverage_type': data.get('coverage_type', 'individual'),
        'needs_maternity': data.get('needs_maternity', False),
        'needs_critical_illness': data.get('needs_critical_illness', False),
        'needs_senior': data.get('needs_senior', False),
        'needs_international': data.get('needs_international', False),
        'needs_topup': data.get('needs_topup', False),
        'has_diabetes': data.get('has_diabetes', False),
        'has_heart_disease': data.get('has_heart_disease', False)
    }
    from src.mlproject.insurance_company_data import filter_plans
    matched = filter_plans(criteria)
    return jsonify({'plans': matched})

@app.route('/admin/gemini-key', methods=['GET', 'POST'])
def admin_gemini_key():
    if request.method == 'POST':
        # Accept key from form data or JSON
        key = None
        if request.form and 'gemini_key' in request.form:
            key = request.form.get('gemini_key')
        elif request.is_json:
            data = request.get_json(silent=True) or {}
            key = data.get('gemini_key')
        if not key:
            return render_template('gemini_key.html', message='Gemini key is required', success=False)
        ok = update_gemini_key(key)
        msg = 'Gemini key updated. Configuration ' + ('succeeded' if ok else 'failed') + '.'
        return render_template('gemini_key.html', message=msg, success=ok)
    # GET request renders a small testing form
    return render_template('gemini_key.html', message=None, success=None)

@app.route('/admin/refresh', methods=['POST'])
def admin_refresh():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({'error': 'Not running with the Werkzeug server'}), 500
    func()
    return jsonify({'status': 'Server is restarting...'}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
