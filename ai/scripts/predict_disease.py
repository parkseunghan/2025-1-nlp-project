import json
import time
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# ✅ 경로
SYMPTOM_LABEL_MAP_PATH = "data/symptom_label_map.json"
DISEASE_LABEL_MAP_PATH = "data/disease_label_map.json"
GUIDELINE_PATH = "data/guideline.json"
SYMPTOM_LIST_PATH = "data/symptoms.json"
SEVERITY_PATH = "processed/merged_symptom_severity.csv"
X_PATH = "processed/X_train.npy"
Y_PATH = "processed/y_train.npy"

# ✅ 데이터 로딩
with open(SYMPTOM_LABEL_MAP_PATH, encoding="utf-8") as f:
    symptom_label_map = {item["id"]: item["ko"] for item in json.load(f)}

with open(DISEASE_LABEL_MAP_PATH, encoding="utf-8") as f:
    label_map = {item["id"]: item["ko"] for item in json.load(f)}

with open(GUIDELINE_PATH, encoding="utf-8") as f:
    guideline_map = json.load(f)

with open(SYMPTOM_LIST_PATH) as f:
    SYMPTOM_LIST = json.load(f)

severity_df = pd.read_csv(SEVERITY_PATH)
severity_dict = dict(zip(severity_df["Symptom"], severity_df["Symptom_severity"]))

X = np.load(X_PATH)
y = np.load(Y_PATH, allow_pickle=True)

# ✅ 디버깅 함수
def debug(title, data):
    print(f"\n🔎 {title}")
    if isinstance(data, (list, dict, np.ndarray)):
        print(data if len(str(data)) < 500 else str(data)[:500] + "...")
    else:
        print(data)

# ✅ 증상 → 벡터 변환 함수
def symptoms_to_vector(symptoms: list[str]) -> np.ndarray:
    debug("입력된 증상 목록", symptoms)
    vector = np.zeros(len(SYMPTOM_LIST))
    for s in symptoms:
        if s in SYMPTOM_LIST:
            vector[SYMPTOM_LIST.index(s)] = 1
    debug("증상 벡터 변환 결과 (numpy 배열)", vector)
    return vector

# ✅ 위험도 계산
def calculate_risk_level(symptoms: list[str]) -> tuple[float, str]:
    weighted_severities = []
    for s in set(symptoms):
        base = severity_dict.get(s, 0)
        multiplier = {
            1: 1.0, 2: 1.0, 3: 1.1, 4: 1.2, 5: 1.4, 6: 1.6, 7: 1.8,
        }.get(base, 1.0)
        weighted = base * multiplier
        weighted_severities.append(weighted)

    total = sum(weighted_severities)
    debug("가중치 적용된 severity", dict(zip(symptoms, weighted_severities)))
    debug("총합 (가중치 적용)", total)

    if total >= 30:
        return round(total, 2), "high"
    elif total >= 15:
        return round(total, 2), "medium"
    else:
        return round(total, 2), "low"

# ✅ 모델 학습
model = RandomForestClassifier(random_state=42)
model.fit(X, y)

# ✅ 증상 기여도 기반 usedSymptoms 계산
def get_contributing_symptoms(disease_label: str, symptoms: list[str], top_k: int = 4) -> list[dict]:
    base_vector = symptoms_to_vector(symptoms)
    base_prob = model.predict_proba(base_vector.reshape(1, -1))[0][list(model.classes_).index(disease_label)]

    contributions = []
    for s in symptoms:
        temp_symptoms = symptoms.copy()
        temp_symptoms.remove(s)
        temp_vector = symptoms_to_vector(temp_symptoms)
        temp_prob = model.predict_proba(temp_vector.reshape(1, -1))[0][list(model.classes_).index(disease_label)]
        delta = base_prob - temp_prob
        contributions.append((s, delta))

    contributions.sort(key=lambda x: x[1], reverse=True)
    return [
        {
            "symptom": sid,
            "korean": symptom_label_map.get(sid, sid)
        }
        for sid, delta in contributions if delta > 0
    ][:top_k]

# ✅ 예측 함수
def predict_disease(symptoms: list[str], top_n: int = 3) -> dict:
    print("\n🧪 예측 시작")
    start = time.time()
    vec = symptoms_to_vector(symptoms).reshape(1, -1)

    probas = model.predict_proba(vec)[0]
    debug("전체 질병별 예측 확률", dict(zip(model.classes_, probas)))

    prob_dict = {label: probas[i] for i, label in enumerate(model.classes_)}
    ranked = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
    debug("Top-N 예측 결과", ranked)

    fine_label = ranked[0][0]
    korean_name = label_map.get(fine_label, fine_label)
    coarse_label = fine_label.split("_")[0]
    risk_score, risk_level = calculate_risk_level(symptoms)
    elapsed = round(time.time() - start, 3)
    guideline = guideline_map.get(fine_label, f"{fine_label}에 대한 가이드라인이 없습니다.")

    return {
        "usedSymptoms": [
            {"symptom": s, "korean": symptom_label_map.get(s, s)} for s in symptoms
        ],
        "koreanLabel": korean_name,
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
                "koreanLabel": label_map.get(d, d),
                "riskScore": round(p, 4),
                "usedSymptoms": get_contributing_symptoms(d, symptoms)
            }
            for i, (d, p) in enumerate(ranked)
        ],
    }

# ✅ 테스트 실행
if __name__ == "__main__":
    test_symptoms = [
        "abdominal_pain",
        "diarrhoea",
        "fever",
        "stomach_pain",
    ]
    result = predict_disease(test_symptoms)

    from pprint import pprint
    print("\n✅ 최종 예측 결과:")
    pprint(result)
