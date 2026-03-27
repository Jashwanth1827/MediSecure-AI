from flask import Flask, request, render_template, jsonify, session
from werkzeug.utils import secure_filename
import os
import tempfile

from src.mlproject.pipelines.prediction_pipeline import CustomData, PredictPipeline
from src.mlproject.medical_report_processor import (
    process_medical_report, 
    get_state_cost_factor, 
    get_state_base_cost,
    update_state_cost_factors,
    INDIAN_STATES_COST_FACTOR
)
from src.mlproject.gemini_chatbot import (
    chat_with_gemini, 
    save_message, 
    save_user_profile, 
    get_chat_history, 
    generate_session_id, 
    GEMINI_CONFIGURED,
    get_user_profile
)

application = Flask(__name__)
app = application
app.secret_key = os.environ.get('SECRET_KEY', 'medisecure-secret-key-12345')

UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

update_state_cost_factors()
INDIAN_STATES = sorted(INDIAN_STATES_COST_FACTOR.keys())

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
                             gemini_configured=GEMINI_CONFIGURED)
    
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
        children = float(request.form.get('children', 0))
        smoker = request.form.get('smoker', 'no')
        state = request.form.get('state', 'maharashtra')
        
        data = CustomData(
            age=age,
            sex=sex,
            bmi=bmi,
            children=children,
            smoker=smoker,
            state=state,
            disease_cost=disease_cost
        )
        
        pred_df = data.get_data_as_data_frame()

        predict_pipeline = PredictPipeline()
        base_prediction = predict_pipeline.predict(pred_df)
        
        state_factor = get_state_cost_factor(state)
        state_base_cost = get_state_base_cost(state)
        final_prediction = (base_prediction[0] * state_factor) + disease_cost
        
        profile = {
            'age': age,
            'sex': sex,
            'bmi': bmi,
            'children': children,
            'smoker': smoker,
            'state': state,
            'diseases': diseases_found,
            'predicted_cost': final_prediction
        }
        save_user_profile(session_id, profile)

        return render_template('index.html', 
                             states=INDIAN_STATES,
                             results="{:.2f}".format(final_prediction),
                             base_cost="{:.2f}".format(base_prediction[0]),
                             state_factor="{:.2f}".format(state_factor),
                             state_base_cost=state_base_cost,
                             disease_cost="{:.2f}".format(disease_cost),
                             diseases_found=diseases_found,
                             severity=severity,
                             disease_details=disease_details,
                             lab_findings=lab_findings,
                             report_summary=report_summary,
                             age=age, 
                             sex=sex, 
                             bmi=bmi, 
                             children=children, 
                             smoker=smoker, 
                             state=state,
                             session_id=session_id,
                             gemini_configured=GEMINI_CONFIGURED)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
