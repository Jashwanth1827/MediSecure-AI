import pandas as pd
import numpy as np

df = pd.read_csv('notebook/data/Health_insurance.csv')

states = [
    'maharashtra', 'karnataka', 'tamil nadu', 'delhi', 'gujarat',
    'rajasthan', 'madhya pradesh', 'west bengal', 'uttar pradesh', 'kerala',
    'andhra pradesh', 'telangana', 'punjab', 'haryana', 'jharkhand',
    'bihar', 'odisha', 'chhattisgarh', 'uttarakhand', 'himachal pradesh',
    'goa', 'puducherry', 'assam', 'meghalaya', 'manipur'
]

np.random.seed(42)
df['state'] = np.random.choice(states, size=len(df))

df = df.drop('region', axis=1)

cols = ['age', 'sex', 'bmi', 'children', 'smoker', 'state', 'charges']
df = df[cols]

df.to_csv('notebook/data/Health_insurance.csv', index=False)

print(f"Dataset updated with {len(states)} Indian states")
print(df.head())
