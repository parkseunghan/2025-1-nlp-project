# 📄 predict_disease.py (증상 하드코딩 버전)
import json
import time
import ast
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

# ✅ 파일 경로
SYMPTOM_LIST_PATH = "data/final_symptom_list.json"
DISEASE_LIST_PATH = "data/final_disease_list.json"
SEVERITY_PATH = "processed/merged_symptom_severity.csv"
TRAIN_PATH = "processed/karthik_train_cleaned.csv"

# ✅ 데이터 로딩
with open(SYMPTOM_LIST_PATH) as f:
    SYMPTOM_LIST = json.load(f)

with open(DISEASE_LIST_PATH) as f:
    DISEASE_LIST = json.load(f)

severity_df = pd.read_csv(SEVERITY_PATH)
severity_dict = dict(zip(severity_df["Symptom"], severity_df["Symptom_severity"]))

train_df = pd.read_csv(TRAIN_PATH)
train_df["cleaned_symptoms"] = train_df["cleaned_symptoms"].apply(ast.literal_eval)


# ✅ 증상 → 벡터 변환 함수
def symptoms_to_vector(symptoms: list[str]) -> np.ndarray:
    vector = np.zeros(len(SYMPTOM_LIST))
    for s in symptoms:
        if s in SYMPTOM_LIST:
            vector[SYMPTOM_LIST.index(s)] = 1
    return vector


# ✅ 위험도 계산 (severity 기반)
def calculate_risk_level(symptoms: list[str]) -> tuple[float, str]:
    severities = [severity_dict.get(s, 0) for s in symptoms]
    total = sum(severities)
    avg = total / len(severities) if severities else 0
    adjusted = total + avg * 1.5
    if adjusted < 5:
        return round(adjusted, 2), "low"
    elif adjusted < 10:
        return round(adjusted, 2), "medium"
    else:
        return round(adjusted, 2), "high"


# ✅ 모델 학습
X = np.array([symptoms_to_vector(s) for s in train_df["cleaned_symptoms"]])
y = train_df["prognosis"]
model = RandomForestClassifier(random_state=42)
model.fit(X, y)


# ✅ 예측 함수
def predict_disease(symptoms: list[str], top_n: int = 3) -> dict:
    start = time.time()
    vec = symptoms_to_vector(symptoms).reshape(1, -1)

    probas = model.predict_proba(vec)[0]
    prob_dict = {label: probas[i] for i, label in enumerate(model.classes_)}
    ranked = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]

    fine_label = ranked[0][0]
    coarse_label = fine_label.split("_")[0]
    risk_score = round(ranked[0][1], 4)
    elapsed = round(time.time() - start, 3)
    risk_val, risk_level = calculate_risk_level(symptoms)
    guideline = f"{fine_label}이 의심됩니다. 수분 섭취, 휴식, 병원 방문 권장."

    return {
        "coarseLabel": coarse_label,
        "fineLabel": fine_label,
        "riskScore": risk_score,
        "riskLevel": risk_level,
        "guideline": guideline,
        "elapsedSec": elapsed,
        "ranks": [
            {
                "rank": i + 1,
                "coarseLabel": d.split("_")[0],
                "fineLabel": d,
                "riskScore": round(p, 4),
            }
            for i, (d, p) in enumerate(ranked)
        ],
    }


# ✅ 실행: 증상 하드코딩
if __name__ == "__main__":
    test_symptoms = ["cough", "chest_pain", "high_fever"]  # 🔧 여기에 원하는 증상 입력
    result = predict_disease(test_symptoms)

    from pprint import pprint

    print("✅ 입력 증상:", test_symptoms)
    pprint(result)
