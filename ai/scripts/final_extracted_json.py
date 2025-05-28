import pandas as pd
import json
from pathlib import Path
from ast import literal_eval
import re

# 매핑 테이블 로드 (정제용)
with open("outputs/mapping_table.json", "r", encoding="utf-8") as f:
    mapping_table = json.load(f)

def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[\s\-_]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text

def apply_mapping(value: str, mapping_dict: dict) -> str:
    norm_value = normalize_text(value)
    return mapping_dict.get(norm_value, norm_value.replace(" ", "_"))

# 초기 세트
input_dir = Path("processed")
diseases_set = set()
symptoms_set = set()

for file in input_dir.glob("*.csv"):
    df = pd.read_csv(file)

    # ✅ 1. 질병 수집
    label_col = "prognosis" if "prognosis" in df.columns else ("Disease" if "Disease" in df.columns else None)
    if label_col:
        disease_values = df[label_col].dropna().astype(str).apply(lambda x: apply_mapping(x, mapping_table["diseases"]))
        diseases_set.update(disease_values)

    # ✅ 2. cleaned_symptoms 리스트 수집
    if "cleaned_symptoms" in df.columns:
        for sym_list in df["cleaned_symptoms"].dropna():
            try:
                symptoms = literal_eval(sym_list) if isinstance(sym_list, str) else sym_list
                if isinstance(symptoms, list):
                    for s in symptoms:
                        symptoms_set.add(apply_mapping(s, mapping_table["symptoms"]))
            except Exception as e:
                print(f"⚠️ 오류 발생: {e} in file {file}")

    # ✅ 3. Symptom_1 ~ Symptom_17 컬럼 수집
    symptom_cols = [col for col in df.columns if col.startswith("Symptom_")]
    for col in symptom_cols:
        values = df[col].dropna().astype(str)
        for v in values:
            if v.lower() != "nan":
                symptoms_set.add(apply_mapping(v, mapping_table["symptoms"]))

# ✅ 정렬 후 저장
disease_list = sorted(diseases_set)
symptom_list = sorted(symptoms_set)

with open("data/final_disease_list.json", "w", encoding="utf-8") as f:
    json.dump(disease_list, f, ensure_ascii=False, indent=2)

with open("data/final_symptom_list.json", "w", encoding="utf-8") as f:
    json.dump(symptom_list, f, ensure_ascii=False, indent=2)

print("✅ 최종 질병 및 증상 리스트 생성 완료!")
