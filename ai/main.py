# main.py

from preprocessing.load_data import load_all_csvs
from preprocessing.data_integrator import merge_all_symptom_datasets
from preprocessing.clean_data import clean_and_save_symptom_data
from preprocessing.build_disease_symptom_map import build_disease_symptom_map
from preprocessing.vectorizer import run_tfidf_vectorizer

# 1. 데이터 로드
datasets = load_all_csvs()

# 2. 통합
df_merged = merge_all_symptom_datasets(datasets)

# 3. 정제 및 저장 (→ processed/merged_symptoms.csv)
clean_and_save_symptom_data(df_merged)

# 4. 질병-증상 매핑 저장 (→ processed/disease_symptom_map.csv)
build_disease_symptom_map()

# 5. TF-IDF 벡터화
run_tfidf_vectorizer()
