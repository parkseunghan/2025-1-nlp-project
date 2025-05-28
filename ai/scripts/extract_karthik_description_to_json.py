# 📄 scripts/extract_karthik_description_to_json.py
# disease_precaution.csv
# pranay_patil_symptom_Description.csv
# pranay_patil_symptom_precaution.csv

import pandas as pd
import json
from pathlib import Path

# 파일 경로
DESC_PATH = Path("data/pranay_patil_symptom_precaution.csv")
EXISTING_JSON_PATH = Path("outputs/pranay_extracted.json")
OUTPUT_PATH = EXISTING_JSON_PATH  # 덮어쓰기

# 기존 JSON 불러오기 (없으면 빈 기본값 생성)
if EXISTING_JSON_PATH.exists():
    with open(EXISTING_JSON_PATH, "r", encoding="utf-8") as f:
        merged_data = json.load(f)
else:
    merged_data = {"diseases": [], "symptoms": []}

# ✅ 1열만 질병
df = pd.read_csv(DESC_PATH)
new_diseases = df.iloc[:, 0].dropna().unique().tolist()

# ✅ 병합 후 중복 제거
merged_data["diseases"] = sorted(set(merged_data["diseases"]) | set(new_diseases))

# ✅ JSON 저장
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=2, ensure_ascii=False)

print(f"✅ 질병 정보 병합 완료: {OUTPUT_PATH}")
print(f"🦠 총 질병 수: {len(merged_data['diseases'])}개")
