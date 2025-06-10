# 📄 scripts/vectorize_and_save.py
import json
import ast
import numpy as np
import pandas as pd

SYMPTOM_LIST_PATH = "data/symptoms.json"
TRAIN_PATH = "processed/karthik_train_cleaned.csv"

with open(SYMPTOM_LIST_PATH) as f:
    SYMPTOM_LIST = json.load(f)

train_df = pd.read_csv(TRAIN_PATH)
train_df["cleaned_symptoms"] = train_df["cleaned_symptoms"].apply(ast.literal_eval)

def symptoms_to_vector(symptoms: list[str]) -> np.ndarray:
    vector = np.zeros(len(SYMPTOM_LIST))
    for s in symptoms:
        if s in SYMPTOM_LIST:
            vector[SYMPTOM_LIST.index(s)] = 1
    return vector

X = np.array([symptoms_to_vector(s) for s in train_df["cleaned_symptoms"]])
y = train_df["prognosis"].to_numpy()

np.save("processed/X_train.npy", X)
np.save("processed/y_train.npy", y)

print("✅ 벡터화 완료: X_train.npy, y_train.npy 저장됨")
