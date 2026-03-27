from flask import Flask, request, render_template, request
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

application = Flask(__name__)
app = application

UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

update_state_cost_factors()
INDIAN_STATES = sorted(INDIAN_STATES_COST_FACTOR.keys())

@app.route('/', methods=['GET', 'POST'])
def predict_datapoint():
    
    if request.method == 'GET':
        return render_template('index.html', states=INDIAN_STATES, results=None)
    
    else:
        disease_cost = 0
        disease_details = []
        diseases_found = []
        severity = 'none'
        lab_findings = {}
        report_summary = ''
        
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
        
        data = CustomData(
            age=float(request.form.get('age')),
            sex=request.form.get('sex'),
            bmi=float(request.form.get('bmi')),
            children=float(request.form.get('children')),
            smoker=request.form.get('smoker'),
            state=request.form.get('state'),
            disease_cost=disease_cost
        )
        
        pred_df = data.get_data_as_data_frame()

        predict_pipeline = PredictPipeline()
        base_prediction = predict_pipeline.predict(pred_df)
        
        state_factor = get_state_cost_factor(data.state)
        state_base_cost = get_state_base_cost(data.state)
        final_prediction = (base_prediction[0] * state_factor) + disease_cost
        
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
                             age=data.age, 
                             sex=data.sex, 
                             bmi=data.bmi, 
                             children=data.children, 
                             smoker=data.smoker, 
                             state=data.state)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
