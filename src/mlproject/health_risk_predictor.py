# =====================================================================
# ARCHITECTURE ROLE: DYNAMIC HEALTH DIAGNOSTICS & RISK FORECASTING
# =====================================================================
# This module implements the preventive health analytic rules of MediSecure.
# It computes a personalized Health Score, projects prospective medical risk 
# distributions, estimates potential premium savings from health improvements,
# and generates structured action plans.
#
# Modularity benefits:
# 1. Separates clinical/preventative diagnostics from underwriting logic.
# 2. Allows upgrading the diagnostic and planning algorithms without touching
#    the model scoring routines or route endpoints.
# =====================================================================

from datetime import datetime
from typing import Dict, List, Optional

DISEASE_IMPACT = {
    'diabetes': {
        'health_score_impact': 25,
        'related_risks': ['heart_disease', 'stroke', 'kidney_disease'],
        'severity_costs': {'mild': 15000, 'moderate': 35000, 'severe': 85000}
    },
    'hypertension': {
        'health_score_impact': 20,
        'related_risks': ['heart_disease', 'stroke', 'kidney_disease'],
        'severity_costs': {'mild': 8000, 'moderate': 20000, 'severe': 55000}
    },
    'heart disease': {
        'health_score_impact': 35,
        'related_risks': ['stroke', 'kidney_disease'],
        'severity_costs': {'mild': 35000, 'moderate': 75000, 'severe': 180000}
    },
    'cancer': {
        'health_score_impact': 45,
        'related_risks': ['heart_disease', 'stroke'],
        'severity_costs': {'mild': 120000, 'moderate': 350000, 'severe': 800000}
    },
    'kidney disease': {
        'health_score_impact': 30,
        'related_risks': ['heart_disease', 'stroke'],
        'severity_costs': {'mild': 45000, 'moderate': 120000, 'severe': 350000}
    },
    'liver disease': {
        'health_score_impact': 30,
        'related_risks': ['cancer', 'heart_disease'],
        'severity_costs': {'mild': 55000, 'moderate': 130000, 'severe': 380000}
    },
    'asthma': {
        'health_score_impact': 15,
        'related_risks': ['respiratory_disease', 'heart_disease'],
        'severity_costs': {'mild': 8000, 'moderate': 22000, 'severe': 55000}
    },
    'copd': {
        'health_score_impact': 25,
        'related_risks': ['heart_disease', 'respiratory_disease'],
        'severity_costs': {'mild': 18000, 'moderate': 45000, 'severe': 120000}
    },
    'arthritis': {
        'health_score_impact': 12,
        'related_risks': ['heart_disease', 'osteoporosis'],
        'severity_costs': {'mild': 12000, 'moderate': 35000, 'severe': 75000}
    },
    'thyroid': {
        'health_score_impact': 10,
        'related_risks': ['heart_disease', 'osteoporosis'],
        'severity_costs': {'mild': 8000, 'moderate': 20000, 'severe': 45000}
    },
    'anemia': {
        'health_score_impact': 8,
        'related_risks': ['heart_disease'],
        'severity_costs': {'mild': 6000, 'moderate': 18000, 'severe': 40000}
    },
    'pneumonia': {
        'health_score_impact': 15,
        'related_risks': ['respiratory_disease', 'heart_disease'],
        'severity_costs': {'mild': 12000, 'moderate': 35000, 'severe': 85000}
    },
    'tuberculosis': {
        'health_score_impact': 20,
        'related_risks': ['respiratory_disease', 'cancer'],
        'severity_costs': {'mild': 25000, 'moderate': 65000, 'severe': 150000}
    },
    'mental health': {
        'health_score_impact': 18,
        'related_risks': ['heart_disease'],
        'severity_costs': {'mild': 15000, 'moderate': 45000, 'severe': 120000}
    },
    'depression': {
        'health_score_impact': 15,
        'related_risks': ['heart_disease', 'mental_health'],
        'severity_costs': {'mild': 12000, 'moderate': 38000, 'severe': 95000}
    },
    'anxiety': {
        'health_score_impact': 12,
        'related_risks': ['heart_disease', 'mental_health'],
        'severity_costs': {'mild': 10000, 'moderate': 32000, 'severe': 85000}
    },
    'stroke': {
        'health_score_impact': 40,
        'related_risks': ['heart_disease', 'kidney_disease'],
        'severity_costs': {'mild': 85000, 'moderate': 180000, 'severe': 450000}
    },
    'dengue': {
        'health_score_impact': 10,
        'related_risks': ['liver_disease'],
        'severity_costs': {'mild': 12000, 'moderate': 35000, 'severe': 85000}
    },
    'malaria': {
        'health_score_impact': 8,
        'related_risks': ['liver_disease', 'kidney_disease'],
        'severity_costs': {'mild': 8000, 'moderate': 22000, 'severe': 65000}
    }
}

RELATED_DISEASES = {
    'diabetes': ['heart_disease', 'stroke', 'kidney_disease', 'retinopathy', 'neuropathy'],
    'hypertension': ['heart_disease', 'stroke', 'kidney_disease', 'vision_loss'],
    'heart_disease': ['stroke', 'kidney_disease', 'peripheral_vascular_disease'],
    'cancer': ['immune_disorder', 'organ_failure'],
    'kidney_disease': ['heart_disease', 'anemia', 'bone_disease'],
    'liver_disease': ['cancer', 'kidney_disease', 'internal_bleeding'],
    'respiratory_disease': ['heart_disease', 'pulmonary_hypertension'],
    'mental_health': ['heart_disease', 'diabetes', 'substance_abuse']
}

def calculate_health_score(profile: Dict, detected_diseases: List[str] = None, severity: str = 'none') -> int:
    base_score = 100
    detected_diseases = detected_diseases or []
    
    age = profile.get('age', 30)
    bmi = profile.get('bmi', 25)
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    
    if age > 70:
        base_score -= 15
    elif age > 60:
        base_score -= 10
    elif age > 50:
        base_score -= 7
    elif age > 40:
        base_score -= 4
    
    if bmi > 35:
        base_score -= 18
    elif bmi > 30:
        base_score -= 12
    elif bmi > 27:
        base_score -= 6
    elif bmi > 24:
        base_score -= 2
    
    if smoker:
        base_score -= 15
    
    for disease in detected_diseases:
        disease_lower = disease.lower().strip()
        for key, info in DISEASE_IMPACT.items():
            if key in disease_lower or disease_lower in key:
                impact = info['health_score_impact']
                if severity == 'severe':
                    impact = int(impact * 1.3)
                elif severity == 'moderate':
                    impact = int(impact * 1.0)
                else:
                    impact = int(impact * 0.7)
                base_score -= impact
                break
    
    return max(0, min(100, base_score))

def predict_health_risks(profile: Dict, detected_diseases: List[str] = None, severity: str = 'none') -> Dict:
    detected_diseases = detected_diseases or []
    risks = []
    
    base_risks = [
        {'disease': 'Cardiovascular Disease', 'base_risk': 15, 'cost': 85000},
        {'disease': 'Type 2 Diabetes', 'base_risk': 12, 'cost': 45000},
        {'disease': 'Stroke', 'base_risk': 8, 'cost': 180000},
        {'disease': 'Respiratory Issues', 'base_risk': 10, 'cost': 45000},
        {'disease': 'Joint Problems', 'base_risk': 12, 'cost': 35000},
        {'disease': 'Kidney Dysfunction', 'base_risk': 7, 'cost': 120000},
        {'disease': 'Liver Complications', 'base_risk': 6, 'cost': 130000},
        {'disease': 'Mental Health Issues', 'base_risk': 15, 'cost': 45000},
        {'disease': 'Bone Density Loss', 'base_risk': 8, 'cost': 35000},
        {'disease': 'Immune System Decline', 'base_risk': 5, 'cost': 75000}
    ]
    
    age = profile.get('age', 30)
    bmi = profile.get('bmi', 25)
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    sex = profile.get('sex', 'male')
    
    detected_lower = [d.lower().strip() for d in detected_diseases]
    
    for risk in base_risks:
        risk_score = risk['base_risk']
        
        if age > 50: risk_score += 10
        elif age > 40: risk_score += 5
        
        if bmi > 30: risk_score += 12
        elif bmi > 27: risk_score += 6
        
        if smoker: risk_score += 15
        
        if 'Cardiovascular' in risk['disease']:
            if any('heart' in d or 'hypertension' in d for d in detected_lower):
                risk_score = 85 + (15 if severity == 'severe' else 5)
            if any('diabetes' in d for d in detected_lower):
                risk_score += 10
        
        if 'Diabetes' in risk['disease']:
            if bmi > 27: risk_score += 15
            if any('diabetes' in d for d in detected_lower):
                risk_score = 85 + (15 if severity == 'severe' else 5)
            if any('heart' in d for d in detected_lower):
                risk_score += 8
        
        if 'Stroke' in risk['disease']:
            if any('hypertension' in d for d in detected_lower):
                risk_score += 20
            if any('heart' in d for d in detected_lower):
                risk_score += 12
            if any('diabetes' in d for d in detected_lower):
                risk_score += 8
        
        if 'Bone Density' in risk['disease']:
            if age > 50: risk_score += 15
            if sex == 'female': risk_score += 8
        
        risk_percentage = min(95, max(5, risk_score))
        
        severity_level = 'High' if risk_percentage > 60 else ('Medium' if risk_percentage > 30 else 'Low')
        
        prevention = get_prevention_tips(risk['disease'])
        
        risks.append({
            'disease': risk['disease'],
            'risk_percentage': risk_percentage,
            'severity': severity_level,
            'prevention': prevention,
            'cost_impact': risk['cost'],
            'detected': any(word.lower() in risk['disease'].lower() for word in detected_lower)
        })
    
    risks.sort(key=lambda x: (x['detected'], x['risk_percentage']), reverse=True)
    
    return {
        'risks': risks,
        'overall_risk_level': get_risk_level(risks, detected_diseases),
        'action_items': generate_action_items(risks, detected_diseases, severity)
    }

def get_prevention_tips(disease: str) -> List[str]:
    tips_map = {
        'Cardiovascular': ['Exercise 30 mins daily', 'Heart-healthy diet', 'Monitor BP regularly', 'Quit smoking'],
        'Diabetes': ['Control carbohydrate intake', 'Regular blood sugar monitoring', 'Maintain healthy weight', 'Annual HbA1c tests'],
        'Stroke': ['Control blood pressure', 'Manage cholesterol', 'Exercise regularly', 'Limit alcohol'],
        'Respiratory': ['Avoid pollution', 'Quit smoking', 'Breathing exercises', 'Annual lung function tests'],
        'Joint': ['Low-impact exercises', 'Maintain healthy weight', 'Calcium supplements', 'Avoid overexertion'],
        'Kidney': ['Stay hydrated', 'Control blood pressure', 'Limit sodium', 'Annual kidney function tests'],
        'Liver': ['Limit alcohol', 'Healthy diet', 'Vaccination for Hepatitis', 'Avoid toxins'],
        'Mental': ['Stress management', 'Regular exercise', 'Adequate sleep', 'Seek therapy when needed'],
        'Bone': ['Calcium & Vitamin D', 'Weight-bearing exercises', 'Prevent falls', 'Bone density tests'],
        'Immune': ['Balanced nutrition', 'Adequate sleep', 'Reduce stress', 'Regular health checkups']
    }
    
    for key, tips in tips_map.items():
        if key in disease:
            return tips[:3]
    return ['Regular health monitoring', 'Healthy lifestyle', 'Annual checkups']

def get_risk_level(risks: List, detected_diseases: List) -> str:
    detected_lower = [d.lower() for d in detected_diseases]
    high_risks = sum(1 for r in risks if r['risk_percentage'] > 60 or r['detected'])
    
    if high_risks >= 3:
        return 'Critical'
    elif high_risks >= 2:
        return 'High'
    elif high_risks >= 1 or any(r['risk_percentage'] > 40 for r in risks):
        return 'Moderate'
    return 'Low'

def generate_action_items(risks: List, detected_diseases: List, severity: str) -> List[str]:
    actions = []
    detected_lower = [d.lower() for d in detected_diseases]
    
    for disease in detected_diseases:
        actions.append(f"Follow up on {disease.title()} - Severity: {severity.title()}")
        actions.append(f"Take prescribed medications regularly")
        actions.append(f"Schedule periodic monitoring for {disease.title()}")
    
    for risk in risks[:4]:
        if risk['risk_percentage'] > 40 and not risk['detected']:
            actions.append(f"Prevent {risk['disease']}: {risk['prevention'][0]}")
    
    return actions[:6]

def get_workout_recommendations(profile: Dict, detected_diseases: List[str] = None, severity: str = 'none') -> Dict:
    detected_diseases = detected_diseases or []
    age = profile.get('age', 30)
    bmi = profile.get('bmi', 25)
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    gender = profile.get('sex', 'male').lower()
    
    # Path A: Medical report is uploaded with conditions
    if len(detected_diseases) > 0:
        detected_lower = [d.lower() for d in detected_diseases]
        
        # If severe, or has critical conditions (heart disease, stroke, cancer) with moderate/severe intensity
        if severity == 'severe' or any(c in d for d in detected_lower for c in ['heart', 'stroke', 'cancer', 'kidney']):
            return {
                'suitability': 'Gentle & Restorative (Low Intensity)',
                'weekly_target': '75 - 120 minutes per week (broken into 10-15 minute daily sessions)',
                'recommended_exercises': [
                    'Short, slow-paced walking on flat surfaces',
                    'Gentle joint rotations and passive stretching',
                    'Seated chair yoga (supported postures only)',
                    'Deep, controlled diaphragmatic breathing exercises (Pranayama)'
                ],
                'precautions': [
                    'CRITICAL: Stop immediately if you experience chest pain, dizziness, or shortness of breath.',
                    'Strictly avoid high-intensity workouts, heavy lifting, or activities that cause rapid heart rate elevation.',
                    'Keep hydration levels stable; do not exercise in extreme heat or cold.',
                    'Consult your primary cardiologist or specialist before starting any new daily routine.'
                ]
            }
        
        # Moderate severity conditions / Standard chronic conditions
        else:
            exercises = []
            precautions = [
                'Warm up for at least 10 minutes before workouts, and cool down for 5-10 minutes.',
                'Stay hydrated: drink 250ml water every 20 minutes of moderate activity.',
                'Monitor heart rate; keep intensity in the low-to-moderate zone (below 60-70% of max heart rate).'
            ]
            
            has_arthritis = any('arthritis' in d for d in detected_lower)
            has_diabetes = any('diabetes' in d for d in detected_lower)
            has_hypertension = any('hypertension' in d or 'bp' in d for d in detected_lower)
            has_asthma_copd = any('asthma' in d or 'copd' in d for d in detected_lower)
            has_mental = any(any(m in d for m in ['mental', 'depression', 'anxiety']) for d in detected_lower)
            
            if has_arthritis:
                exercises.extend([
                    'Swimming or water aerobics (minimizes joint weight-bearing load)',
                    'Low-resistance stationary cycling (maintains knee/hip joint range of motion)',
                    'Gentle hamstring and quad stretches to support knee joints'
                ])
                precautions.append('Avoid high-impact jumping, running, or heavy weighted leg extensions that stress joint cartilage.')
            
            if has_diabetes:
                exercises.extend([
                    'Brisk walking or light jogging (30 mins daily helps improve insulin sensitivity)',
                    'Light resistance band exercises (promotes glucose uptake in skeletal muscles)',
                    'Yoga (helps manage cortisol levels and metabolic stress)'
                ])
                precautions.append('Check blood sugar before exercising; keep fast-acting carbohydrates (glucose tablets/juice) nearby.')
                
            if has_hypertension:
                exercises.extend([
                    'Steady-state walking, light cycling, or elliptical training',
                    'Low-weight, high-repetition circuit training (avoid straining)',
                    'Mindful stretching and deep breathing to aid autonomic relaxation'
                ])
                precautions.append('Avoid heavy lifting, isometric holds (like planks), and holding your breath (Valsalva maneuver) which spike BP.')
                
            if has_asthma_copd:
                exercises.extend([
                    'Indoor walking or light stationary cycling (minimizes pollen/cold exposure)',
                    'Pursed-lip breathing exercises and intercostal muscle stretches',
                    'Interval training (short walking bursts followed by adequate recovery)'
                ])
                precautions.append('Always carry your rescue inhaler on your person; avoid working out in cold, dry air or high-pollen days.')
                
            if has_mental:
                exercises.extend([
                    'Outdoor walking/jogging in nature (proven to reduce stress and anxiety)',
                    'Group fitness classes or recreational sports (boosts social connectivity and mood)',
                    'Vinyasa yoga or tai chi (improves body-mind coherence and reduces cortisol)'
                ])
                
            # Default fallback if none of the above specific cases matched but there are other diseases
            if not exercises:
                exercises.extend([
                    'Brisk walking on a flat surface or treadmill',
                    'Basic bodyweight movements (seated sit-to-stands, wall pushups)',
                    'Stretching routine for major muscle groups (legs, back, shoulders)'
                ])
                
            return {
                'suitability': 'Moderate & Controlled Aerobic (Low-to-Medium Intensity)',
                'weekly_target': '120 - 150 minutes per week (e.g., 30 mins, 4-5 days a week)',
                'recommended_exercises': list(dict.fromkeys(exercises))[:4], # limit to 4 unique items
                'precautions': list(dict.fromkeys(precautions))[:4]
            }

    # Path B: No medical report (Demographic metric-based plan)
    else:
        # Age-based and BMI-based categorization
        if age > 55:
            return {
                'suitability': 'Active Longevity & Joint Mobility (Low Intensity)',
                'weekly_target': '150 minutes per week of low-impact physical activity',
                'recommended_exercises': [
                    'Brisk walking or slow trail walks',
                    'Low-impact swimming or water walking (protects older joints)',
                    'Tai Chi or balance training (essential for fall prevention)',
                    'Gentle flexibility stretching for spine, hips, and shoulders'
                ],
                'precautions': [
                    'Focus on balance and joint stability to prevent falls.',
                    'Keep exercises low-impact; avoid heavy pounding on knees and lower back.',
                    'Ensure proper hydration and warm up thoroughly before movement.',
                    'If joint pain arises, rest and modify exercises to avoid aggravating inflammation.'
                ]
            }
        
        elif bmi > 28:
            return {
                'suitability': 'Low-Impact Cardio & Core Stability (Moderate Intensity)',
                'weekly_target': '150 - 200 minutes per week of calorie-burning activity',
                'recommended_exercises': [
                    'Stationary cycling or elliptical training (low joint impact)',
                    'Water swimming or pool walking (reduces weight-bearing stress by up to 90%)',
                    'Core stability training (planks, bird-dogs) to support lower back',
                    'Light resistance training using machine-supported weights'
                ],
                'precautions': [
                    'Avoid high-impact jumping, hard running, or deep knee bends to protect joints.',
                    'Wear well-cushioned, supportive athletic footwear.',
                    'Focus on consistency and gradual progression rather than intense bursts.',
                    'Monitor knee alignment: ensure knees do not cave inward during squats.'
                ]
            }
            
        elif smoker:
            return {
                'suitability': 'Cardiorespiratory Stamina & Lung Restoration (Moderate Intensity)',
                'weekly_target': '150 minutes per week of aerobic and breathing exercises',
                'recommended_exercises': [
                    'Progressive cardio intervals (alternating 3 mins walk with 1 min light jog)',
                    'Indoor rowing or swimming (utilizes full body, improving oxygen delivery)',
                    'Incentive spirometry or pursed-lip deep breathing techniques',
                    'Moderate bodyweight strength circuits (improves peripheral oxygen usage)'
                ],
                'precautions': [
                    'Expect quicker onset of shortness of breath; take regular breaks as needed.',
                    'Always warm up the respiratory tract: start with 5-10 mins of very light movement.',
                    'Avoid training in environments with high dust, smoke, or cold dry drafts.',
                    'Stay hydrated to help thin mucus and ease airway passage during workouts.'
                ]
            }
            
        else:
            # Default healthy general profile
            return {
                'suitability': 'Active Fitness & Strength Training (Medium-to-High Intensity)',
                'weekly_target': '150 - 300 minutes per week of mixed aerobic and strength work',
                'recommended_exercises': [
                    'Cardiovascular exercises (jogging, cycling, rowing, or swimming)',
                    'Strength training (barbells, dumbbells, or bodyweight pullups/pushups)',
                    'High-Intensity Interval Training (HIIT) once or twice weekly',
                    'Dynamic flexibility and core strengthening routines'
                ],
                'precautions': [
                    'Maintain proper form and posture, especially during heavy lifts.',
                    'Allow 48 hours of recovery between intense training of the same muscle groups.',
                    'Warm up for 5-10 minutes; never skip the post-workout static stretch.',
                    'Stay hydrated and consume balanced meals to fuel muscle recovery.'
                ]
            }

def calculate_premium_savings(profile: Dict, detected_diseases: List[str] = None, severity: str = 'none') -> Dict:
    detected_diseases = detected_diseases or []
    health_score = calculate_health_score(profile, detected_diseases, severity)
    
    age = profile.get('age', 30)
    bmi = profile.get('bmi', 25)
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    
    base_premium = 35000
    
    if age > 50: base_premium += 12000
    elif age > 40: base_premium += 7000
    elif age > 35: base_premium += 3000
    
    if len(detected_diseases) > 0:
        if severity == 'severe':
            base_premium += 25000 * len(detected_diseases)
        elif severity == 'moderate':
            base_premium += 12000 * len(detected_diseases)
        else:
            base_premium += 5000 * len(detected_diseases)
    
    potential_savings = {
        'quit_smoking': 8000 if smoker else 0,
        'reduce_bmi': int(base_premium * 0.12) if bmi > 27 else 0,
        'disease_management': int(base_premium * 0.08) if len(detected_diseases) > 0 else 0,
        'preventive_care': int(base_premium * 0.05),
        'healthy_lifestyle': int(base_premium * 0.07)
    }
    
    total_savings = sum(potential_savings.values())
    workout_rec = get_workout_recommendations(profile, detected_diseases, severity)
    
    return {
        'current_annual': int(base_premium),
        'potential_savings': potential_savings,
        'total_annual_savings': total_savings,
        'savings_projection': {
            '1_year': int(total_savings * 1.1),
            '3_years': int(total_savings * 3.5),
            '5_years': int(total_savings * 6)
        },
        'health_score': health_score,
        'detected_diseases': detected_diseases,
        'severity': severity,
        'tips': get_personalized_tips(profile, detected_diseases, severity),
        'workout_recommendations': workout_rec
    }

def get_personalized_tips(profile: Dict, detected_diseases: List[str], severity: str) -> List[str]:
    tips = []
    detected_lower = [d.lower() for d in detected_diseases]
    smoker = profile.get('smoker', 'no').lower() == 'yes'
    bmi = profile.get('bmi', 25)
    
    if smoker:
        tips.append("URGENT: Quit smoking - reduces heart disease risk by 50%")
    
    if bmi > 27:
        tips.append(f"Target: Reduce BMI from {bmi} to 25 - saves Rs. 4000+/year")
    
    for disease in detected_diseases:
        disease_lower = disease.lower()
        
        if 'diabetes' in disease_lower:
            tips.append("Diabetes Care: Monitor blood sugar daily, follow low-GI diet")
        elif 'hypertension' in disease_lower:
            tips.append("BP Control: Reduce salt intake, exercise 30 mins daily")
        elif 'heart' in disease_lower:
            tips.append("Heart Health: Cardiac-friendly diet, regular ECG monitoring")
        elif 'thyroid' in disease_lower:
            tips.append("Thyroid: Regular T3/T4 tests, avoid goitrogenic foods")
        elif 'mental' in disease_lower or 'depression' in disease_lower:
            tips.append("Mental Wellness: Daily meditation, therapy sessions")
    
    if severity == 'severe':
        tips.append("CRITICAL: Regular specialist consultations required")
        tips.append("Keep emergency contacts and medication list handy")
    elif severity == 'moderate':
        tips.append("Schedule follow-up tests within 3 months")
    
    tips.append("Annual comprehensive health checkup - claim 80D tax benefit")
    
    return tips[:5]

def generate_prevention_plan(profile: Dict, detected_diseases: List[str] = None, severity: str = 'none') -> Dict:
    detected_diseases = detected_diseases or []
    health_score = calculate_health_score(profile, detected_diseases, severity)
    
    detected_lower = [d.lower() for d in detected_diseases]
    
    plan = {
        'patient_profile': {
            'age': profile.get('age', 30),
            'bmi': profile.get('bmi', 25),
            'lifestyle': 'High Risk' if profile.get('smoker') == 'yes' else ('Moderate' if len(detected_diseases) > 0 else 'Low Risk'),
            'health_score': health_score,
            'detected_conditions': detected_diseases,
            'severity': severity.title() if severity else 'None'
        },
        'immediate_actions': [],
        'monthly_plan': [],
        'quarterly_goals': [],
        'annual_milestones': []
    }
    
    if len(detected_diseases) > 0:
        plan['immediate_actions'].append({
            'task': f'Consult specialist for {", ".join(detected_diseases[:2])}',
            'impact': 'Critical for managing diagnosed conditions',
            'timeline': 'Within 1 week'
        })
        plan['immediate_actions'].append({
            'task': 'Get baseline tests done for all detected conditions',
            'impact': 'Establishes monitoring parameters',
            'timeline': 'Within 2 weeks'
        })
        plan['immediate_actions'].append({
            'task': 'Review and understand all prescribed medications',
            'impact': 'Ensures proper adherence',
            'timeline': 'Immediately'
        })
    else:
        plan['immediate_actions'].append({
            'task': 'Schedule comprehensive health checkup',
            'impact': 'Early detection saves lakhs',
            'timeline': 'This month'
        })
        plan['immediate_actions'].append({
            'task': 'Review vaccination status',
            'impact': 'Prevention is better than cure',
            'timeline': 'This week'
        })
    
    plan['monthly_plan'] = [
        {'month': 1, 'goals': ['Complete baseline tests', 'Start prescribed medications', 'Track daily symptoms']},
        {'month': 2, 'goals': ['Follow up on test results', 'Adjust lifestyle if needed', 'Monitor progress']},
        {'month': 3, 'goals': ['Review medication effectiveness', 'Diet modifications', 'Exercise routine']}
    ]
    
    detected_names = [d.title() for d in detected_diseases] if detected_diseases else ['General Health']
    
    plan['quarterly_goals'] = [
        {'quarter': 'Q1', 'target': f'Manage {", ".join(detected_names[:2])}', 'tests': ['Condition-specific blood tests', 'Imaging if required']},
        {'quarter': 'Q2', 'target': 'Improve health score by 10 points', 'tests': ['Lipid Profile', 'HbA1c', 'Liver Function']},
        {'quarter': 'Q3', 'target': 'Achieve target weight/BMI', 'tests': ['Body Composition', 'ECG']},
        {'quarter': 'Q4', 'target': 'Annual comprehensive assessment', 'tests': ['Full Health Checkup', 'Specialist Consultations']}
    ]
    
    savings = calculate_premium_savings(profile, detected_diseases, severity)
    
    plan['annual_milestones'] = [
        {'year': 1, 'target': f'Reduce risk factors by 20%', 'savings': f'Rs. {savings["savings_projection"]["1_year"]:,}'},
        {'year': 2, 'target': 'Stabilize all detected conditions', 'savings': f'Rs. {savings["savings_projection"]["3_years"]:,}'},
        {'year': 3, 'target': 'Achieve optimal health management', 'savings': f'Rs. {savings["savings_projection"]["5_years"]:,}'}
    ]
    
    return plan

def get_ai_insights(profile: Dict, detected_diseases: List[str] = None, severity: str = 'none') -> str:
    health_score = calculate_health_score(profile, detected_diseases or [], severity)
    detected = detected_diseases or []
    
    insights = []
    
    insights.append(f"Health Score: {health_score}/100")
    
    if health_score >= 80:
        insights.append("Excellent health - maintain current lifestyle")
    elif health_score >= 60:
        insights.append("Good health - minor improvements recommended")
    elif health_score >= 40:
        insights.append("Moderate health - attention needed on detected conditions")
    else:
        insights.append("Health needs urgent attention - follow medical advice")
    
    if len(detected) > 0:
        insights.append(f"Active Conditions: {', '.join([d.title() for d in detected])}")
        if severity == 'severe':
            insights.append("Priority: Strict condition management required")
        elif severity == 'moderate':
            insights.append("Focus: Regular monitoring and medication")
        else:
            insights.append("Action: Lifestyle modifications + monitoring")
    
    return " | ".join(insights)
