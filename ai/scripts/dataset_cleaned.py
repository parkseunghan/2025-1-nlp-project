import pandas as pd
import os
import json
from pathlib import Path
import re

# 매핑 테이블 불러오기
with open("outputs/mapping_table.json", "r", encoding="utf-8") as f:
    mapping_table = json.load(f)

# 텍스트 정규화
def normalize_text(text: str) -> str:
    text = text.strip().lower()
    return text


# 매핑 적용
def apply_mapping(value: str, mapping_dict: dict) -> str:
    norm = normalize_text(value)
    return mapping_dict.get(norm, norm.replace(" ", "_"))

# 벡터 구조 처리 (증상 열: 0/1, 라벨 열 있음)
def clean_vector_dataset(filepath, label_col, output_path):
    df = pd.read_csv(filepath)
    symptom_cols = [c for c in df.columns if c != label_col and not c.lower().startswith("unnamed")]

    # 0/1 벡터 → 증상 리스트
    def extract(row):
        return [apply_mapping(col, mapping_table["symptoms"])
                for col in symptom_cols if str(row[col]) == "1"]
    
    df["cleaned_symptoms"] = df.apply(extract, axis=1)
    df[label_col] = df[label_col].astype(str).apply(lambda x: apply_mapping(x, mapping_table["diseases"]))
    df[[label_col, "cleaned_symptoms"]].to_csv(output_path, index=False)

# 클래식 구조 처리 (Symptom_1 ~ Symptom_17)
def clean_classic_dataset(filepath, label_col, output_path):
    df = pd.read_csv(filepath)
    symptom_cols = [col for col in df.columns if col.startswith("Symptom_")]
    for col in symptom_cols:
        df[col] = df[col].astype(str).apply(lambda x: apply_mapping(x, mapping_table["symptoms"]) if x.lower() != "nan" else "")
    df[label_col] = df[label_col].astype(str).apply(lambda x: apply_mapping(x, mapping_table["diseases"]))
    df.to_csv(output_path, index=False)

# Yes/No 증상 열 처리 (Laksika)
def clean_laksika_binary_dataset(filepath, label_col, symptom_cols, output_path):
    df = pd.read_csv(filepath)

    # Yes/No → 1/0
    for col in symptom_cols:
        df[col] = df[col].map({"Yes": 1, "No": 0, "yes": 1, "no": 0}).fillna(0).astype(int)
    
    def extract(row):
        return [apply_mapping(col, mapping_table["symptoms"]) for col in symptom_cols if row[col] == 1]

    df["cleaned_symptoms"] = df.apply(extract, axis=1)
    df[label_col] = df[label_col].astype(str).apply(lambda x: apply_mapping(x, mapping_table["diseases"]))
    df[[label_col, "cleaned_symptoms"]].to_csv(output_path, index=False)

# 저장 폴더
output_dir = Path("processed")
output_dir.mkdir(exist_ok=True)

# 실행 예시
clean_vector_dataset("data/karthik_udyawer_Training.csv", "prognosis", output_dir / "karthik_train_cleaned.csv")
clean_vector_dataset("data/karthik_udyawer_Testing.csv", "prognosis", output_dir / "karthik_test_cleaned.csv")
clean_classic_dataset("data/karthik_udyawer_dataset.csv", "Disease", output_dir / "karthik_dataset_cleaned.csv")
clean_vector_dataset("data/kaushil268_Training.csv", "prognosis", output_dir / "kaushil_train_cleaned.csv")
clean_vector_dataset("data/kaushil268_Testing.csv", "prognosis", output_dir / "kaushil_test_cleaned.csv")
clean_classic_dataset("data/pranay_patil_dataset.csv", "Disease", output_dir / "pranay_cleaned.csv")
clean_laksika_binary_dataset(
    filepath="data/laksika_Disease_symptom_and_patient_profile_dataset.csv",
    label_col="Disease",
    symptom_cols=["Fever", "Cough", "Fatigue", "Difficulty Breathing"],
    output_path=output_dir / "laksika_cleaned.csv"
)
