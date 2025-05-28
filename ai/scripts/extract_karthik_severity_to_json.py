# 📄 scripts/extract_karthik_severity_to_json.py
# pranay_patil_Symptom-severity.csv

import pandas as pd
import json
from pathlib import Path

# 파일 경로
SEVERITY_PATH = Path("data/pranay_patil_Symptom-severity.csv")
EXISTING_JSON_PATH = Path("outputs/pranay_extracted.json")
OUTPUT_PATH = EXISTING_JSON_PATH  # 덮어쓰기

# 기존 JSON 불러오기 (없으면 빈 기본값 생성)
if EXISTING_JSON_PATH.exists():
    with open(EXISTING_JSON_PATH, "r", encoding="utf-8") as f:
        merged_data = json.load(f)
else:
    merged_data = {"diseases": [], "symptoms": []}

# ✅ 1열만 증상
df = pd.read_csv(SEVERITY_PATH)
new_symptoms = df.iloc[:, 0].dropna().unique().tolist()

# ✅ 병합 후 중복 제거
merged_data["symptoms"] = sorted(set(merged_data["symptoms"]) | set(new_symptoms))

# ✅ JSON 저장
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=2, ensure_ascii=False)

print(f"✅ 증상 정보 병합 완료: {OUTPUT_PATH}")
print(f"🧩 총 증상 수: {len(merged_data['symptoms'])}개")
