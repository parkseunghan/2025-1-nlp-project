# 📄 generate_disease_symptom_mapping.py

import pandas as pd
import ast
import json
from pathlib import Path
from collections import defaultdict

# ✅ cleaned CSV 파일 경로들
paths = [
    "processed/karthik_train_cleaned.csv",
    "processed/karthik_test_cleaned.csv",
    "processed/laksika_cleaned.csv",
    "processed/pranay_cleaned.csv",
    "processed/kaushil_train_cleaned.csv",
    "processed/kaushil_test_cleaned.csv"
]

# ✅ 질병 → 증상 매핑 테이블 초기화
disease_symptom_map = defaultdict(list)

# ✅ 모든 파일에서 증상 수집
for path in paths:
    df = pd.read_csv(path)
    if "cleaned_symptoms" not in df.columns or "prognosis" not in df.columns:
        continue

    # 리스트 형태 문자열을 실제 리스트로 파싱
    df["cleaned_symptoms"] = df["cleaned_symptoms"].apply(ast.literal_eval)

    for _, row in df.iterrows():
        disease = row["prognosis"]
        symptoms = row["cleaned_symptoms"]
        disease_symptom_map[disease].extend(symptoms)

# ✅ 중복 제거 및 정렬
for disease in disease_symptom_map:
    unique_symptoms = sorted(set(disease_symptom_map[disease]))
    disease_symptom_map[disease] = unique_symptoms

# ✅ JSON 저장
output_path = "data/disease_symptom_mapping.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(disease_symptom_map, f, ensure_ascii=False, indent=2)

print(f"✅ 매핑 완료: {output_path}")
