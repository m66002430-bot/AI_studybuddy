import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

# ---------------- DATASET ----------------

data = {
    "marks": [
        40, 45, 50, 55, 60,
        65, 70, 75, 80, 85,
        90, 95, 35, 48, 58,
        68, 73, 78, 88, 92
    ],

    "attendance": [
        60, 65, 70, 72, 75,
        78, 80, 82, 85, 88,
        90, 92, 55, 68, 73,
        79, 84, 87, 91, 95
    ],

    "study_hours": [
        1, 1.5, 2, 2, 2.5,
        3, 3, 3.5, 4, 4,
        4.5, 5, 1, 1.5, 2.5,
        3, 3.5, 4, 4.5, 5
    ],

    "performance": [
        45, 48, 52, 57, 62,
        67, 72, 76, 81, 86,
        91, 95, 40, 51, 60,
        70, 75, 80, 89, 93
    ]
}

df = pd.DataFrame(data)

# ---------------- FEATURES & TARGET ----------------

X = df[["marks", "attendance", "study_hours"]]
y = df["performance"]

# ---------------- TRAIN MODEL ----------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()

model.fit(X_train, y_train)

# ---------------- SAVE MODEL ----------------

joblib.dump(model, "performance_model.pkl")

print("ML Model trained successfully!")
print("Model saved as performance_model.pkl")