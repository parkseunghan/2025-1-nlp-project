import pandas as pd

# 🔹 파일 경로 (로컬에 맞게 수정 가능)
pranay_path = "data/pranay_patil_Symptom-severity.csv"
karthik_path = "data/karthik_udyawer_symptom_severity.csv"
output_path = "processed/merged_symptom_severity.csv"

# 🔹 1. 파일 로드
pranay_df = pd.read_csv(pranay_path)
karthik_df = pd.read_csv(karthik_path)

# 🔹 2. 컬럼명 통일
pranay_df.columns = ["Symptom", "Symptom_severity"]
karthik_df.columns = ["Symptom", "Symptom_severity"]

# 🔹 3. 증상명 정규화 함수
def normalize_symptom(sym):
    return sym.strip().lower().replace(" ", "_").replace("-", "_")

pranay_df["Symptom"] = pranay_df["Symptom"].apply(normalize_symptom)
karthik_df["Symptom"] = karthik_df["Symptom"].apply(normalize_symptom)

# 🔹 4. 병합 + 중복 증상 평균 처리
merged_df = pd.concat([pranay_df, karthik_df])
merged_df = merged_df.groupby("Symptom", as_index=False)["Symptom_severity"].mean()

# 🔹 5. 결과 저장
merged_df.to_csv(output_path, index=False, encoding="utf-8")
print(f"✅ 병합된 symptom severity 저장 완료 → {output_path}")
