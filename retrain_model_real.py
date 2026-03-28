import numpy as np
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error

print("Loading enhanced dataset...")
df = pd.read_csv('notebook/data/Health_insurance.csv')

print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

target = 'charges'
X = df.drop(columns=[target, 'new_premium'], axis=1)
y = df[target]

print(f"\nFeatures: {X.columns.tolist()}")
print(f"Target: {target}")
print(f"Shape: {X.shape}")

num_features = X.select_dtypes(exclude="object").columns.tolist()
cat_features = X.select_dtypes(include="object").columns.tolist()

print(f"\nNumerical features: {num_features}")
print(f"Categorical features: {cat_features}")

numeric_transformer = StandardScaler()
oh_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

preprocessor = ColumnTransformer(
    [
        ("num_pipeline", numeric_transformer, num_features),
        ("cat_pipeline", oh_transformer, cat_features),
    ]
)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\nTransforming data...")
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

print("Training model...")
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_transformed, y_train)

train_score = model.score(X_train_transformed, y_train)
test_score = model.score(X_test_transformed, y_test)

y_train_pred = model.predict(X_train_transformed)
y_test_pred = model.predict(X_test_transformed)

train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)

print(f"\n=== Model Performance ===")
print(f"Training R2 Score: {train_score:.4f}")
print(f"Test R2 Score: {test_score:.4f}")
print(f"Training MAE: {train_mae:.2f}")
print(f"Test MAE: {test_mae:.2f}")

os.makedirs('artifacts', exist_ok=True)

model_path = 'artifacts/model.pkl'
preprocessor_path = 'artifacts/preprocessor.pkl'

print(f"\nSaving model to {model_path}...")
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"Saving preprocessor to {preprocessor_path}...")
with open(preprocessor_path, 'wb') as f:
    pickle.dump(preprocessor, f)

print("\n=== Feature Importances ===")
feature_names = (
    num_features + 
    list(preprocessor.named_transformers_['cat_pipeline'].get_feature_names_out(cat_features))
)
importances = model.feature_importances_
for name, importance in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
    print(f"  {name}: {importance:.4f}")

print("\nTraining complete!")
print(f"Model saved to: {model_path}")
print(f"Preprocessor saved to: {preprocessor_path}")
