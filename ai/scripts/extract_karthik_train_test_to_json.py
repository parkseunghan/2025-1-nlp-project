# 📄 scripts/extract_karthik_train_test_to_json.py
# kaushil268
import pandas as pd
import json
from pathlib import Path

# 경로 설정
FILES = [
    Path("data/kaushil268_Training.csv"),
    Path("data/kaushil268_Testing.csv"),
]
EXISTING_JSON_PATH = Path("outputs/kaushi268_extracted.json")
OUTPUT_PATH = EXISTING_JSON_PATH  # 덮어쓰기

# 기존 JSON 불러오기
if EXISTING_JSON_PATH.exists():
    with open(EXISTING_JSON_PATH, "r", encoding="utf-8") as f:
        merged_data = json.load(f)
else:
    merged_data = {"diseases": [], "symptoms": []}

all_diseases = set(merged_data["diseases"])
all_symptoms = set(merged_data["symptoms"])

# 파일별 처리
for file in FILES:
    df = pd.read_csv(file)

    # 마지막 열이 질병
    disease_col = df.columns[-1]
    diseases = df[disease_col].dropna().unique().tolist()
    all_diseases.update(diseases)

    # 나머지 열은 증상
    symptom_cols = df.columns[:-1].tolist()
    all_symptoms.update(symptom_cols)

# 병합 후 저장
merged_data["diseases"] = sorted(all_diseases)
merged_data["symptoms"] = sorted(all_symptoms)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=2, ensure_ascii=False)

print(f"✅ 질병 및 증상 병합 완료: {OUTPUT_PATH}")
print(f"🦠 총 질병 수: {len(merged_data['diseases'])}개")
print(f"🧩 총 증상 수: {len(merged_data['symptoms'])}개")
