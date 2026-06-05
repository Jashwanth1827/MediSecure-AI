# =====================================================================
# ARCHITECTURE ROLE: MACHINE LEARNING & RISK UNDERWRITING PIPELINE
# =====================================================================
# This module encapsulates the business rules and ML logic for insurance
# pricing. It defines insurance multipliers (Sum Insured, Policy Term, Room
# Type, Deductible, Co-pay, NCB, and Region Zone multipliers) and handles
# loading the saved Random Forest model and preprocessor pipelines.
#
# Modularity benefits:
# 1. Isolates data scaling and inference code from the Flask API routes.
# 2. Encapsulates risk calculation rules in Python classes.
# =====================================================================

import sys
import os
import pandas as pd
from src.mlproject.exception import CustomException
from src.mlproject.utils import load_object


SUM_INSURED_FACTORS = {
    '5_lakhs': 1.0,
    '10_lakhs': 1.35,
    '15_lakhs': 1.65,
    '25_lakhs': 2.0,
    '50_lakhs': 2.8,
    '1_crore': 3.5,
}

POLICY_TERM_FACTORS = {
    '1_year': 1.0,
    '2_year': 1.85,
    '3_year': 2.6,
}

ROOM_TYPE_FACTORS = {
    'general': 1.0,
    'semi_private': 1.25,
    'private': 1.5,
}

DEDUCTIBLE_FACTORS = {
    '0': 1.0,
    '25000': 0.85,
    '50000': 0.75,
    '100000': 0.65,
    '200000': 0.55,
}

COPAY_FACTORS = {
    '0': 1.0,
    '10': 0.92,
    '15': 0.88,
    '20': 0.85,
    '25': 0.82,
}

NCB_FACTORS = {
    '0': 1.0,
    '20': 0.95,
    '25': 0.93,
    '33': 0.90,
    '45': 0.85,
    '50': 0.80,
}

RIDER_FACTORS = {
    'none': 0,
    'basic': 1500,
    'comprehensive': 3500,
    'premium': 6000,
}

RIDER_BENEFITS = {
    'none': [],
    'basic': ['Personal Accident'],
    'comprehensive': ['Personal Accident', 'Critical Illness', 'Hospital Cash'],
    'premium': ['Personal Accident', 'Critical Illness', 'Hospital Cash', 'Ambulance', 'Worldwide Coverage']
}

ZONE_MULTIPLIERS = {
    'A': 1.15,
    'B': 1.0,
    'C': 0.88,
}

STATE_ZONES = {
    'delhi': 'A', 'maharashtra': 'A', 'karnataka': 'A', 'tamil nadu': 'A', 'telangana': 'A',
    'gujarat': 'A', 'west bengal': 'A',
    'punjab': 'B', 'haryana': 'B', 'rajasthan': 'B', 'odisha': 'B', 'bihar': 'B',
    'madhya pradesh': 'B', 'uttar pradesh': 'B', 'jharkhand': 'B', 'chhattisgarh': 'B',
    'kerala': 'B', 'andhra pradesh': 'B', 'uttarakhand': 'B',
    'assam': 'C', 'himachal pradesh': 'C', 'goa': 'C', 'puducherry': 'C', 'jammu and kashmir': 'C',
    'meghalaya': 'C', 'manipur': 'C', 'nagaland': 'C', 'tripura': 'C', 'sikkim': 'C',
    'arunachal pradesh': 'C', 'mizoram': 'C', 'ladakh': 'C', 'chandigarh': 'B',
}

ZONE_CITIES = {
    'A': ['Delhi NCR', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata'],
    'B': ['Pune', 'Ahmedabad', 'Surat', 'Jaipur', 'Chandigarh', 'Lucknow'],
    'C': ['Other Cities', 'Tier 2/3 Towns', 'Rural Areas'],
}


class PredictPipeline:
    def __init__(self):
        pass

    def predict(self, features):
        try:
            model_path = os.path.join("artifacts", "model.pkl")
            preprocessor_path = os.path.join('artifacts', 'preprocessor.pkl')
            print("Loading model and preprocessor...")
            model = load_object(file_path=model_path)
            preprocessor = load_object(file_path=preprocessor_path)
            print("Transformation complete")
            data_scaled = preprocessor.transform(features)
            preds = model.predict(data_scaled)
            return preds
        
        except Exception as e:
            raise CustomException(e, sys)


class CustomData:
    def __init__(self,
                 age: int,
                 sex: str,
                 bmi: float,
                 children: int,
                 smoker: str,
                 state: str,
                 sum_insured: str = '10_lakhs',
                 policy_term: str = '1_year',
                 room_type: str = 'general',
                 deductible: str = '0',
                 copay: str = '0',
                 ncb: str = '0',
                 riders: str = 'none',
                 disease_cost: float = 0,
                 disease_count: int = 0,
                 severity: str = 'none'):

        self.age = age
        self.sex = sex
        self.bmi = bmi
        self.children = children
        self.smoker = smoker
        self.state = state
        self.sum_insured = sum_insured
        self.policy_term = policy_term
        self.room_type = room_type
        self.deductible = deductible
        self.copay = copay
        self.ncb = ncb
        self.riders = riders
        self.disease_cost = disease_cost
        self.disease_count = disease_count
        self.severity = severity

    def calculate_premium_modifiers(self):
        modifiers = {}
        
        modifiers['sum_insured_factor'] = SUM_INSURED_FACTORS.get(self.sum_insured, 1.0)
        modifiers['policy_term_factor'] = POLICY_TERM_FACTORS.get(self.policy_term, 1.0)
        modifiers['room_type_factor'] = ROOM_TYPE_FACTORS.get(self.room_type, 1.0)
        modifiers['deductible_factor'] = DEDUCTIBLE_FACTORS.get(self.deductible, 1.0)
        modifiers['copay_factor'] = COPAY_FACTORS.get(self.copay, 1.0)
        modifiers['ncb_factor'] = NCB_FACTORS.get(self.ncb, 1.0)
        modifiers['rider_cost'] = RIDER_FACTORS.get(self.riders, 0)
        
        zone = STATE_ZONES.get(self.state.lower(), 'B')
        modifiers['zone_factor'] = ZONE_MULTIPLIERS.get(zone, 1.0)
        modifiers['zone'] = zone
        
        age_loading = 1.0
        if self.age > 50:
            age_loading = 1.25
        elif self.age > 40:
            age_loading = 1.15
        elif self.age > 35:
            age_loading = 1.08
        modifiers['age_loading'] = age_loading
        
        bmi_loading = 1.0
        if self.bmi > 35:
            bmi_loading = 1.20
        elif self.bmi > 30:
            bmi_loading = 1.12
        elif self.bmi > 27:
            bmi_loading = 1.05
        modifiers['bmi_loading'] = bmi_loading
        
        smoker_loading = 1.0
        if self.smoker.lower() == 'yes':
            smoker_loading = 1.40
        modifiers['smoker_loading'] = smoker_loading
        
        disease_loading = 1.0
        if self.disease_count > 0:
            if self.severity == 'severe':
                disease_loading = 1.80
            elif self.severity == 'moderate':
                disease_loading = 1.35
            else:
                disease_loading = 1.15
        modifiers['disease_loading'] = disease_loading
        
        return modifiers

    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict = {
                "age": [self.age],
                "sex": [self.sex],
                "bmi": [self.bmi],
                "children": [self.children],
                "smoker": [self.smoker],
                "state": [self.state],
                "sum_insured": [self.sum_insured],
                "policy_term": [self.policy_term],
                "room_type": [self.room_type],
                "deductible": [self.deductible],
                "copay": [self.copay],
                "ncb": [self.ncb],
                "riders": [self.riders],
            }
            return pd.DataFrame(custom_data_input_dict)
        except Exception as e:
            raise CustomException(e, sys)


def calculate_final_premium(base_prediction, modifiers, disease_cost):
    base = base_prediction
    
    premium = (base 
               * modifiers['sum_insured_factor']
               * modifiers['zone_factor']
               * modifiers['age_loading']
               * modifiers['bmi_loading']
               * modifiers['smoker_loading']
               * modifiers['disease_loading']
               * modifiers['deductible_factor']
               * modifiers['copay_factor']
               * modifiers['ncb_factor'])
    
    annual_premium = premium / modifiers['policy_term_factor']
    
    rider_cost = modifiers['rider_cost']
    
    final_premium = annual_premium + rider_cost + disease_cost
    
    return max(final_premium, 3000)


def get_coverage_details(sum_insured, riders):
    coverage = {
        'base': [
            'Hospitalization expenses',
            'Day care procedures',
            'Pre & Post hospitalization',
            'Ambulance charges',
            'Organ donor expenses'
        ]
    }
    
    rider_list = RIDER_BENEFITS.get(riders, [])
    coverage['riders'] = rider_list
    
    if sum_insured in ['25_lakhs', '50_lakhs', '1_crore']:
        coverage['additional'] = [
            'International second opinion',
            'Air ambulance cover',
            'Wellness benefits',
            'Mental health cover',
            'Alternative treatments'
        ]
    
    return coverage


def get_sum_insured_display(value):
    return value.replace('_', ' ').replace('lakhs', ' Lakhs').replace('crore', ' Crore').title()


def get_term_display(value):
    return value.replace('_', ' ').title()
