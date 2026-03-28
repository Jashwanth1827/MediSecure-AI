import pandas as pd
import numpy as np

print("Creating enhanced insurance dataset with real premium factors...")

df = pd.read_csv('notebook/data/Health_insurance.csv')

print(f"Original dataset: {len(df)} records")

np.random.seed(42)

df['sum_insured'] = np.random.choice(
    ['5_lakhs', '10_lakhs', '15_lakhs', '25_lakhs', '50_lakhs', '1_crore'],
    size=len(df),
    p=[0.25, 0.35, 0.15, 0.12, 0.08, 0.05]
)

df['policy_term'] = np.random.choice(
    ['1_year', '2_year', '3_year'],
    size=len(df),
    p=[0.60, 0.25, 0.15]
)

df['room_type'] = np.random.choice(
    ['general', 'semi_private', 'private'],
    size=len(df),
    p=[0.55, 0.30, 0.15]
)

df['deductible'] = np.random.choice(
    ['0', '25000', '50000', '100000', '200000'],
    size=len(df),
    p=[0.45, 0.20, 0.18, 0.12, 0.05]
)

df['copay'] = np.random.choice(
    ['0', '10', '15', '20', '25'],
    size=len(df),
    p=[0.50, 0.20, 0.15, 0.10, 0.05]
)

df['ncb'] = np.random.choice(
    ['0', '20', '25', '33', '45', '50'],
    size=len(df),
    p=[0.40, 0.15, 0.15, 0.15, 0.10, 0.05]
)

df['riders'] = np.random.choice(
    ['none', 'basic', 'comprehensive', 'premium'],
    size=len(df),
    p=[0.35, 0.30, 0.25, 0.10]
)

sum_insured_factors = {
    '5_lakhs': 1.0, '10_lakhs': 1.35, '15_lakhs': 1.65,
    '25_lakhs': 2.0, '50_lakhs': 2.8, '1_crore': 3.5
}
policy_term_factors = {'1_year': 1.0, '2_year': 1.85, '3_year': 2.6}
room_type_factors = {'general': 1.0, 'semi_private': 1.25, 'private': 1.5}
deductible_factors = {'0': 1.0, '25000': 0.85, '50000': 0.75, '100000': 0.65, '200000': 0.55}
copay_factors = {'0': 1.0, '10': 0.92, '15': 0.88, '20': 0.85, '25': 0.82}
ncb_factors = {'0': 1.0, '20': 0.95, '25': 0.93, '33': 0.90, '45': 0.85, '50': 0.80}
rider_costs = {'none': 0, 'basic': 1500, 'comprehensive': 3500, 'premium': 6000}

state_zones = {
    'delhi': 1.15, 'maharashtra': 1.15, 'karnataka': 1.12, 'tamil nadu': 1.10,
    'telangana': 1.10, 'gujarat': 1.08, 'west bengal': 1.08,
    'punjab': 1.0, 'haryana': 1.0, 'rajasthan': 0.98, 'odisha': 0.95,
    'bihar': 0.92, 'madhya pradesh': 0.95, 'uttar pradesh': 0.95,
    'jharkhand': 0.92, 'chhattisgarh': 0.92, 'kerala': 1.02, 'andhra pradesh': 0.98,
    'uttarakhand': 0.95, 'assam': 0.88, 'himachal pradesh': 0.90, 'goa': 1.05,
    'puducherry': 0.98, 'jammu and kashmir': 0.92, 'meghalaya': 0.88,
    'manipur': 0.88, 'nagaland': 0.88, 'tripura': 0.88, 'sikkim': 0.88,
    'arunachal pradesh': 0.88, 'mizoram': 0.88, 'ladakh': 0.90, 'chandigarh': 1.02
}

df['base_premium'] = df['charges']

df['zone_factor'] = df['state'].map(state_zones).fillna(1.0)
df['sum_insured_factor'] = df['sum_insured'].map(sum_insured_factors)
df['term_factor'] = df['policy_term'].map(policy_term_factors)
df['room_factor'] = df['room_type'].map(room_type_factors)
df['deductible_factor'] = df['deductible'].map(deductible_factors)
df['copay_factor'] = df['copay'].map(copay_factors)
df['ncb_factor'] = df['ncb'].map(ncb_factors)
df['rider_cost'] = df['riders'].map(rider_costs)

age_loading = np.where(df['age'] > 50, 1.25,
               np.where(df['age'] > 40, 1.15,
               np.where(df['age'] > 35, 1.08, 1.0)))

bmi_loading = np.where(df['bmi'] > 35, 1.20,
              np.where(df['bmi'] > 30, 1.12,
              np.where(df['bmi'] > 27, 1.05, 1.0)))

smoker_loading = np.where(df['smoker'] == 'yes', 1.40, 1.0)

df['premium_modifier'] = (
    df['zone_factor'] * 
    df['sum_insured_factor'] * 
    age_loading * 
    bmi_loading * 
    smoker_loading *
    df['deductible_factor'] *
    df['copay_factor'] *
    df['ncb_factor']
)

df['new_premium'] = (df['base_premium'] * df['premium_modifier'] / df['term_factor'] + df['rider_cost']).round(2)

columns_order = [
    'age', 'sex', 'bmi', 'children', 'smoker', 'state',
    'sum_insured', 'policy_term', 'room_type', 'deductible',
    'copay', 'ncb', 'riders', 'charges', 'new_premium'
]
df = df[[col for col in columns_order if col in df.columns]]

df.to_csv('notebook/data/Health_insurance.csv', index=False)

print(f"\nDataset updated with {len(df)} records!")
print(f"\nNew columns added:")
print(df.columns.tolist())

print("\n\nPremium Distribution Summary:")
print(f"Min Premium: ₹{df['new_premium'].min():,.0f}")
print(f"Max Premium: ₹{df['new_premium'].max():,.0f}")
print(f"Avg Premium: ₹{df['new_premium'].mean():,.0f}")
print(f"Median Premium: ₹{df['new_premium'].median():,.0f}")

print("\n\nSum Insured Distribution:")
print(df['sum_insured'].value_counts())

print("\n\nPolicy Term Distribution:")
print(df['policy_term'].value_counts())

print("\n\nRiders Distribution:")
print(df['riders'].value_counts())
