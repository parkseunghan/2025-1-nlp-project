# 📄 scripts/extract_karthik_dataset_to_json.py

import pandas as pd
import json
from pathlib import Path

# 경로 설정
DATA_PATH = Path("data/karthik_udyawer_dataset.csv")
OUTPUT_PATH = Path("outputs/karthik_extracted.json")
OUTPUT_PATH.parent.mkdir(exist_ok=True)

# 데이터 불러오기
df = pd.read_csv(DATA_PATH)

# ✅ 1. 질병 추출
diseases = sorted(df.iloc[:, 0].dropna().unique())

# ✅ 2. 증상 추출 (Symptom_으로 시작하는 컬럼 값들)
symptom_columns = [col for col in df.columns if col.startswith("Symptom_")]
symptom_set = set()

for col in symptom_columns:
    symptom_set.update(df[col].dropna().unique())

symptoms = sorted(symptom_set)

# ✅ JSON 저장
data = {
    "diseases": diseases,
    "symptoms": symptoms
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ 질병 및 증상 추출 완료: {OUTPUT_PATH}")
print(f"🦠 질병 수: {len(diseases)}개, 💉 증상 수: {len(symptoms)}개")
