import numpy as np
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

df = pd.read_csv('notebook/data/Health_insurance.csv')
print("Dataset loaded with columns:", df.columns.tolist())

X = df.drop(columns=['charges'], axis=1)
y = df['charges']

print("Features:", X.columns.tolist())
print("Shape:", X.shape)

num_features = X.select_dtypes(exclude="object").columns.tolist()
cat_features = X.select_dtypes(include="object").columns.tolist()

print("Numerical features:", num_features)
print("Categorical features:", cat_features)

numeric_transformer = StandardScaler()
oh_transformer = OneHotEncoder(handle_unknown='ignore')

preprocessor = ColumnTransformer(
    [
        ("num_pipeline", numeric_transformer, num_features),
        ("cat_pipeline", oh_transformer, cat_features),
    ]
)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

print("Training model...")

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_transformed, y_train)

train_score = model.score(X_train_transformed, y_train)
test_score = model.score(X_test_transformed, y_test)

print(f"Training R2 Score: {train_score:.4f}")
print(f"Test R2 Score: {test_score:.4f}")

os.makedirs('artifacts', exist_ok=True)

model_path = 'artifacts/model.pkl'
preprocessor_path = 'artifacts/preprocessor.pkl'

with open(model_path, 'wb') as f:
    pickle.dump(model, f)

with open(preprocessor_path, 'wb') as f:
    pickle.dump(preprocessor, f)

print(f"Model saved to {model_path}")
print(f"Preprocessor saved to {preprocessor_path}")
print("Training complete!")
