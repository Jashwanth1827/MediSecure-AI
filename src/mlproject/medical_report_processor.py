# =====================================================================
# ARCHITECTURE ROLE: MEDICAL REPORT PARSING & UNDERWRITING (PDF Service)
# =====================================================================
# This module is responsible for processing health reports. It parses text 
# from PDFs, runs regular expressions to extract laboratory readings, checks
# for pre-existing disease keywords, and calculates medical surcharges.
#
# Modularity benefits:
# 1. Keeps external PDF library dependencies (like PyPDF2) isolated here.
# 2. Allows updating disease lookup dictionaries or parsing logic (e.g.,
#    moving from regex to clinical Named Entity Recognition / NLP models) 
#    without affecting app.py or the ML pipelines.
# =====================================================================

import pandas as pd
import numpy as np
import re
import sys
import os
import requests
from datetime import datetime

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not installed. Installing...")
    os.system("pip install PyPDF2")
    import PyPDF2

DISEASE_SEVERITY_COSTS = {
    'diabetes': {'mild': 15000, 'moderate': 45000, 'severe': 85000},
    'hypertension': {'mild': 8000, 'moderate': 25000, 'severe': 55000},
    'heart disease': {'mild': 35000, 'moderate': 85000, 'severe': 180000},
    'cancer': {'mild': 120000, 'moderate': 350000, 'severe': 800000},
    'kidney disease': {'mild': 45000, 'moderate': 120000, 'severe': 350000},
    'liver disease': {'mild': 55000, 'moderate': 130000, 'severe': 380000},
    'asthma': {'mild': 8000, 'moderate': 22000, 'severe': 55000},
    'copd': {'mild': 18000, 'moderate': 45000, 'severe': 120000},
    'arthritis': {'mild': 12000, 'moderate': 35000, 'severe': 75000},
    'thyroid': {'mild': 8000, 'moderate': 20000, 'severe': 45000},
    'anemia': {'mild': 6000, 'moderate': 18000, 'severe': 40000},
    'pneumonia': {'mild': 12000, 'moderate': 35000, 'severe': 85000},
    'tuberculosis': {'mild': 25000, 'moderate': 65000, 'severe': 150000},
    'mental health': {'mild': 15000, 'moderate': 45000, 'severe': 120000},
    'depression': {'mild': 12000, 'moderate': 38000, 'severe': 95000},
    'anxiety': {'mild': 10000, 'moderate': 32000, 'severe': 85000},
    'stroke': {'mild': 85000, 'moderate': 180000, 'severe': 450000},
    'dengue': {'mild': 12000, 'moderate': 35000, 'severe': 85000},
    'malaria': {'mild': 8000, 'moderate': 22000, 'severe': 65000},
}

DISEASE_KEYWORDS = {
    'diabetes': ['diabetes', 'diabetic', 'blood sugar', 'glucose', 'hbA1c', 'insulin', 'type 1', 'type 2', 'diabetic neuropathy', 'diabetic retinopathy'],
    'hypertension': ['hypertension', 'high blood pressure', 'bp', 'blood pressure', 'hypertensive', 'elevated bp'],
    'heart disease': ['heart disease', 'cardiac', 'cardiovascular', 'coronary', 'arrhythmia', 'heart failure', 'cardiac arrest', 'angina', 'myocardial infarction', 'chest pain', 'cardiac arrhythmia'],
    'cancer': ['cancer', 'tumor', 'malignant', 'carcinoma', 'oncology', 'lymphoma', 'leukemia', 'metastasis', 'neoplasm', 'chemotherapy', 'radiation therapy'],
    'kidney disease': ['kidney disease', 'renal', 'dialysis', 'creatinine', 'gfr', 'nephropathy', 'kidney failure', 'chronic kidney disease', 'uremia'],
    'liver disease': ['liver disease', 'hepatic', 'hepatitis', 'cirrhosis', 'liver function', 'hepatomegaly', 'liver failure', 'fatty liver'],
    'asthma': ['asthma', 'respiratory', 'bronchial', 'wheezing', 'bronchitis', 'respiratory distress'],
    'copd': ['copd', 'chronic obstructive', 'emphysema', 'bronchitis', 'chronic bronchitis', 'lung disease'],
    'arthritis': ['arthritis', 'joint pain', 'osteoarthritis', 'rheumatoid', 'rheumatoid arthritis', 'joint swelling', 'gout'],
    'thyroid': ['thyroid', 'hypothyroidism', 'hyperthyroidism', 'tsh', 'thyroid disorder', 'goiter', 'thyroiditis'],
    'anemia': ['anemia', 'hemoglobin', 'iron deficiency', 'low hemoglobin', 'iron deficiency anemia', 'sickle cell'],
    'pneumonia': ['pneumonia', 'lung infection', 'respiratory infection', 'bronchopneumonia', 'lobar pneumonia'],
    'tuberculosis': ['tuberculosis', 'tb', 'pulmonary tuberculosis', 'extrapulmonary tb'],
    'mental health': ['mental health', 'psychiatric', 'bipolar', 'schizophrenia', 'mental illness', 'psychosis'],
    'depression': ['depression', 'depressive', 'sadness', 'low mood', 'major depressive disorder', 'clinical depression', 'persistent depressive disorder'],
    'anxiety': ['anxiety', 'anxious', 'panic', 'gad', 'generalized anxiety', 'anxiety disorder', 'panic disorder', 'social anxiety'],
    'stroke': ['stroke', 'cerebrovascular accident', 'cva', 'brain attack', 'ischemic stroke', 'hemorrhagic stroke', 'thrombosis'],
    'dengue': ['dengue', 'dengue fever', 'dengue hemorrhagic fever', 'breakbone fever'],
    'malaria': ['malaria', 'malarial', 'plasmodium', 'malaria parasite', 'antimalarial'],
}

SEVERITY_INDICATORS = {
    'mild': ['mild', 'early stage', 'stage 1', 'grade 1', 'low risk', 'controlled', 'stable', 'minor', 'asymptomatic', 'preliminary', 'borderline'],
    'moderate': ['moderate', 'stage 2', 'grade 2', 'medium risk', 'requires monitoring', 'partially controlled', 'intermediate', 'managed', 'chronic'],
    'severe': ['severe', 'stage 3', 'stage 4', 'grade 3', 'grade 4', 'high risk', 'critical', 'uncontrolled', 'advanced', 'terminal', 'aggressive', 'life threatening', 'acute', 'emergency', 'icu', 'critical care']
}

LAB_VALUE_INDICATORS = {
    'high': ['high', 'elevated', 'increased', 'above normal', 'above range', 'positive', '++', '+++', '++++'],
    'low': ['low', 'decreased', 'reduced', 'below normal', 'below range', 'negative', '--', '---']
}

BASE_HEALTHCARE_COST_PER_CAPITA = 45000

INDIAN_STATES_COST_FACTOR = {
    'delhi': 1.85,
    'maharashtra': 1.75,
    'karnataka': 1.65,
    'tamil nadu': 1.55,
    'gujarat': 1.45,
    'kerala': 1.60,
    'telangana': 1.50,
    'andhra pradesh': 1.45,
    'punjab': 1.40,
    'haryana': 1.45,
    'rajasthan': 1.35,
    'west bengal': 1.30,
    'uttar pradesh': 1.25,
    'madhya pradesh': 1.20,
    'odisha': 1.25,
    'jharkhand': 1.15,
    'chhattisgarh': 1.15,
    'bihar': 1.10,
    'assam': 1.15,
    'uttarakhand': 1.30,
    'himachal pradesh': 1.35,
    'goa': 1.70,
    'puducherry': 1.50,
    'chandigarh': 1.55,
    'arunachal pradesh': 1.20,
    'meghalaya': 1.15,
    'manipur': 1.15,
    'mizoram': 1.20,
    'nagaland': 1.15,
    'tripura': 1.10,
    'sikkim': 1.25,
    'jammu and kashmir': 1.25,
    'ladakh': 1.30,
}

def fetch_latest_healthcare_costs():
    try:
        response = requests.get(
            'https://api.worldbank.org/v2/country/IN/indicator/SH.XPD.CHEX.PC.CD?format=json&per_page=1',
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and data[1]:
                return data[1][0].get('value', BASE_HEALTHCARE_COST_PER_CAPITA)
    except Exception:
        pass
    return BASE_HEALTHCARE_COST_PER_CAPITA

def update_state_cost_factors():
    global INDIAN_STATES_COST_FACTOR
    
    base_cost = fetch_latest_healthcare_costs()
    
    state_budget_priority = {
        'delhi': 6.0, 'maharashtra': 5.5, 'karnataka': 6.2, 'tamil nadu': 6.5,
        'gujarat': 5.8, 'kerala': 6.8, 'telangana': 6.0, 'andhra pradesh': 7.0,
        'punjab': 5.5, 'haryana': 5.8, 'rajasthan': 7.5, 'west bengal': 5.2,
        'uttar pradesh': 5.2, 'madhya pradesh': 5.5, 'odisha': 5.8, 'jharkhand': 5.0,
        'chhattisgarh': 5.2, 'bihar': 4.8, 'assam': 5.0, 'uttarakhand': 5.5,
        'himachal pradesh': 5.8, 'goa': 6.0, 'puducherry': 6.2, 'chandigarh': 5.5,
        'arunachal pradesh': 4.5, 'meghalaya': 4.8, 'manipur': 4.5, 'mizoram': 5.0,
        'nagaland': 4.5, 'tripura': 4.8, 'sikkim': 5.2, 'jammu and kashmir': 5.5,
        'ladakh': 5.0,
    }
    
    avg_priority = sum(state_budget_priority.values()) / len(state_budget_priority)
    
    for state in INDIAN_STATES_COST_FACTOR:
        priority = state_budget_priority.get(state, avg_priority)
        INDIAN_STATES_COST_FACTOR[state] = round(0.8 + (priority / avg_priority) * 0.5, 2)
    
    return INDIAN_STATES_COST_FACTOR

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        if isinstance(pdf_file, str):
            pdf_reader = PyPDF2.PdfReader(pdf_file)
        else:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + " "
        return text.lower()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def extract_lab_values(text):
    """Extract and analyze laboratory values from the report"""
    lab_findings = {}
    
    lab_patterns = {
        'blood_sugar': r'(?:blood sugar|glucose|fasting sugar|post prandial|pp sugar)[:\s]+(\d+(?:\.\d+)?)',
        'hba1c': r'hba1c[:\s]+(\d+(?:\.\d+)?)',
        'blood_pressure_systolic': r'(?:bp|blood pressure)[:\s]+(\d+)/(\d+)',
        'creatinine': r'creatinine[:\s]+(\d+(?:\.\d+)?)',
        'gfr': r'gfr[:\s]+(\d+(?:\.\d+)?)',
        'hemoglobin': r'hemoglobin[:\s]+(\d+(?:\.\d+)?)',
        'tsh': r'tsh[:\s]+(\d+(?:\.\d+)?)',
        'wbc': r'wbc[:\s]+(\d+(?:\.\d+)?)',
        'platelets': r'platelets[:\s]+(\d+(?:\.\d+)?)',
    }
    
    for lab_name, pattern in lab_patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            lab_findings[lab_name] = matches
    
    return lab_findings

def analyze_lab_severity(lab_findings):
    """Analyze laboratory values to determine severity"""
    severity_indicators = {'mild': 0, 'moderate': 0, 'severe': 0}
    
    critical_ranges = {
        'blood_sugar': {'severe': [('>', 300), ('<', 50)], 'moderate': [('>', 200), ('<', 70)], 'mild': [('>', 126)]},
        'hba1c': {'severe': [('>', 10)], 'moderate': [('>', 8)], 'mild': [('>', 6.5)]},
        'hemoglobin': {'severe': [('<', 7)], 'moderate': [('<', 10)], 'mild': [('<', 12)]},
        'creatinine': {'severe': [('>', 3)], 'moderate': [('>', 1.5)], 'mild': [('>', 1.2)]},
        'gfr': {'severe': [('<', 30)], 'moderate': [('<', 60)], 'mild': [('<', 90)]},
        'tsh': {'severe': [('>', 20), ('<', 0.1)], 'moderate': [('>', 10), ('<', 0.5)], 'mild': [('>', 4.5)]},
    }
    
    for lab_name, value_matches in lab_findings.items():
        if lab_name in critical_ranges:
            try:
                if lab_name == 'blood_pressure_systolic':
                    continue
                value = float(value_matches[0][0] if isinstance(value_matches[0], tuple) else value_matches[0])
                ranges = critical_ranges[lab_name]
                
                for threshold in ranges.get('severe', []):
                    if threshold[0] == '>' and value > threshold[1]:
                        severity_indicators['severe'] += 2
                    elif threshold[0] == '<' and value < threshold[1]:
                        severity_indicators['severe'] += 2
                
                for threshold in ranges.get('moderate', []):
                    if threshold[0] == '>' and value > threshold[1]:
                        severity_indicators['moderate'] += 1
                    elif threshold[0] == '<' and value < threshold[1]:
                        severity_indicators['moderate'] += 1
            except (ValueError, IndexError):
                continue
    
    return severity_indicators

def detect_diseases(text):
    """Detect diseases mentioned in the medical report with confidence scores"""
    detected_diseases = {}
    
    for disease, keywords in DISEASE_KEYWORDS.items():
        match_count = 0
        matched_keywords = []
        for keyword in keywords:
            if keyword in text:
                match_count += 1
                matched_keywords.append(keyword)
        
        if match_count > 0:
            confidence = min(match_count / len(keywords) * 3, 1.0)
            detected_diseases[disease] = {
                'confidence': confidence,
                'matched_keywords': matched_keywords
            }
    
    return detected_diseases

def detect_severity(text, lab_findings=None):
    """Detect severity level from the text and lab values"""
    severity_scores = {'mild': 0, 'moderate': 0, 'severe': 0}
    
    for severity, indicators in SEVERITY_INDICATORS.items():
        for indicator in indicators:
            if indicator in text:
                severity_scores[severity] += 1
    
    if lab_findings:
        lab_severity = analyze_lab_severity(lab_findings)
        severity_scores['mild'] += lab_severity['mild']
        severity_scores['moderate'] += lab_severity['moderate']
        severity_scores['severe'] += lab_severity['severe']
    
    if severity_scores['severe'] > 0:
        return 'severe'
    elif severity_scores['moderate'] > 0:
        return 'moderate'
    elif severity_scores['mild'] > 0:
        return 'mild'
    return 'mild'

def calculate_disease_cost(diseases_confidence, overall_severity):
    """Calculate additional cost based on diseases and severity with confidence weighting"""
    total_cost = 0
    disease_details = []
    
    for disease, info in diseases_confidence.items():
        confidence = info.get('confidence', 1.0)
        severity_for_disease = overall_severity
        
        if disease in DISEASE_SEVERITY_COSTS:
            base_cost = DISEASE_SEVERITY_COSTS[disease].get(severity_for_disease, 0)
            adjusted_cost = int(base_cost * confidence)
            total_cost += adjusted_cost
            disease_details.append({
                'disease': disease,
                'severity': severity_for_disease,
                'additional_cost': adjusted_cost,
                'confidence': round(confidence * 100, 1),
                'matched_keywords': info.get('matched_keywords', [])
            })
    
    return total_cost, disease_details

def process_medical_report(pdf_file):
    """Main function to process medical report PDF with enhanced analysis"""
    if pdf_file is None or pdf_file == '':
        return {
            'diseases': [],
            'severity': 'none',
            'additional_cost': 0,
            'disease_details': [],
            'lab_findings': {},
            'report_summary': 'No medical report uploaded'
        }
    
    text = extract_text_from_pdf(pdf_file)
    
    if not text:
        return {
            'diseases': [],
            'severity': 'none',
            'additional_cost': 0,
            'disease_details': [],
            'lab_findings': {},
            'report_summary': 'Unable to extract text from PDF'
        }
    
    lab_findings = extract_lab_values(text)
    diseases_confidence = detect_diseases(text)
    overall_severity = detect_severity(text, lab_findings)
    additional_cost, disease_details = calculate_disease_cost(diseases_confidence, overall_severity)
    
    detected_diseases = list(diseases_confidence.keys())
    
    if lab_findings:
        summary_parts = []
        if detected_diseases:
            summary_parts.append(f"Conditions detected: {', '.join(detected_diseases).title()}")
        summary_parts.append(f"Severity assessment: {overall_severity.upper()}")
        summary_parts.append(f"Lab values analyzed: {', '.join(lab_findings.keys()).replace('_', ' ').title()}")
        report_summary = " | ".join(summary_parts)
    else:
        report_summary = f"Conditions detected: {', '.join(detected_diseases).title()}" if detected_diseases else "No significant conditions detected"
    
    return {
        'diseases': detected_diseases,
        'severity': overall_severity,
        'additional_cost': additional_cost,
        'disease_details': disease_details,
        'lab_findings': {k: v[0] if len(v) == 1 else v for k, v in lab_findings.items()},
        'report_summary': report_summary
    }

def get_state_cost_factor(state):
    """Get the cost factor for a given Indian state"""
    return INDIAN_STATES_COST_FACTOR.get(state.lower(), 1.0)

def get_state_base_cost(state):
    """Get the estimated base healthcare cost for a given state"""
    base_cost = BASE_HEALTHCARE_COST_PER_CAPITA
    state_factor = get_state_cost_factor(state)
    return int(base_cost * state_factor)

if __name__ == "__main__":
    print("Medical Report Processing Module")
    print("Available diseases:", list(DISEASE_SEVERITY_COSTS.keys()))
    print("Available states:", len(INDIAN_STATES_COST_FACTOR), "states")
