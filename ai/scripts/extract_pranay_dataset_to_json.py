# 📄 scripts/extract_pranay_dataset_to_json.py

import pandas as pd
import json
from pathlib import Path

# 경로 설정
FILE_PATH = Path("data/pranay_patil_dataset.csv")
EXISTING_JSON_PATH = Path("outputs/pranay_extracted.json")
OUTPUT_PATH = EXISTING_JSON_PATH  # 덮어쓰기

# 기존 JSON 불러오기
if EXISTING_JSON_PATH.exists():
    with open(EXISTING_JSON_PATH, "r", encoding="utf-8") as f:
        merged_data = json.load(f)
else:
    merged_data = {"diseases": [], "symptoms": []}

# ✅ 1. 데이터 불러오기
df = pd.read_csv(FILE_PATH)

# ✅ 2. 질병 추출
diseases = df.iloc[:, 0].dropna().unique().tolist()

# ✅ 3. 증상 추출: "Symptom_"으로 시작하는 컬럼명만
symptom_columns = [col for col in df.columns if col.lower().startswith("symptom_")]

# ✅ 4. 병합 및 중복 제거
merged_data["diseases"] = sorted(set(merged_data["diseases"]) | set(diseases))
merged_data["symptoms"] = sorted(set(merged_data["symptoms"]) | set(symptom_columns))

# ✅ 5. 저장
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=2, ensure_ascii=False)

print(f"✅ 병합 완료: {OUTPUT_PATH}")
print(f"🦠 총 질병 수: {len(merged_data['diseases'])}개")
print(f"🧩 총 증상 수: {len(merged_data['symptoms'])}개")
