import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# === Load Dataset ===
df = pd.read_csv("heart.csv")  # make sure your CSV file name matches

# === Check columns ===
print("Columns in dataset:", df.columns.tolist())

# === Define target column ===
target_col = 'condition'  # Updated from 'num' → 'condition'

# === Convert target to binary (if needed) ===
df[target_col] = (df[target_col] > 0).astype(int)

# === Define features and target ===
X = df.drop(columns=[target_col])
y = df[target_col]

# === Split into training and testing sets ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Train Random Forest Model ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# === Evaluate accuracy ===
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Model training complete! Accuracy: {acc * 100:.2f}%")

# === Save model to file ===
joblib.dump(model, "heart_model.pkl")
print("💾 Model saved as heart_model.pkl")

# === Feature order (for reference during prediction) ===
print("\nFeature order used for prediction:")
print(list(X.columns))
