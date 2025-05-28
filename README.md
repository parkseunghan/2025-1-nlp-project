# 실행 방법
```sh
# 1
cd ai

py -3.9 -m venv venv

source venv/Scripts/activate

pip install -r requirements.txt

py main.py

# 1-1
pip freeze > uninstall.txt
pip uninstall -y -r uninstall.txt

# 2
cd ai

./start.sh



```

# 폴더 구조
ai/
├── main.py                          ▶ 메인 실행 파일
├── requirements.txt                ▶ 필요한 라이브러리 목록
├── start.sh                        ▶ 실행 스크립트 (선택사항)
├── README.md                       ▶ 프로젝트 설명
├── ai/
│   ├── data/                       ▶ 원본 CSV 데이터
│   ├── logs/                       ▶ 로그 저장 폴더 (사용 시 생성)
│   ├── model/
│   │   └── train_mlp_model.py     ▶ MLP 질병 분류 모델 학습 파일
│   ├── preprocessing/
│   │   ├── generate_symptom_map.py▶ 정규화 맵 자동 생성기
│   │   ├── load_data.py           ▶ CSV 로더
│   │   └── utils.py               ▶ 유틸 함수 모음 (정규화 등)
│   ├── processed/
│   │   └── symptom_normalization_map.json ▶ 정규화 맵 결과
│   └── utils/
│       └── logger.py              ▶ 공통 로거


`유틸 모듈 작성`
utils/logger.py: 로그 출력 모듈 (모든 단계에서 사용)

`데이터셋 로딩`
preprocessing/load_data.py: 데이터셋 구조에 따라 CSV 파일 자동 로드 + __source_dataset__, __file_name__ 컬럼 추가

# 실행 흐름
✅ Step 1. load_data.py
모든 CSV 파일을 로드하여 Dict[str, pd.DataFrame] 형태로 반환

파일 위치, 행 개수 등 로그 출력 포함

병렬로 여러 데이터셋 처리 가능

✅ Step 2. data_integrator.py
질병-증상 구조의 파일들만 선별하여 증상 단위로 통합

각 행은 [Disease, Symptom, __source_dataset__] 형식

중복 제거 X → 모든 raw 증상 포함

✅ Step 3. clean_data.py
증상 텍스트 정규화 및 소문자화 (normalize_symptom)

병합 증상 데이터셋의 중복 제거

최종 결과는 processed/merged_symptoms.csv로 저장

✅ Step 4. build_disease_symptom_map.py
각 질병마다 증상의 등장 횟수를 카운팅

구조: [Disease, Symptom, Count]

결과는 processed/disease_symptom_map.csv로 저장

✅ Step 5. generate_symptom_map.py
정제된 증상 리스트를 기반으로 유사 표현 없이 기본 정규화 맵 생성

향후 한글 → 영어 → 벡터화 파이프라인에서 사용

결과는 processed/symptom_normalization_map.json로 저장됨


# 산출물
| 파일명                                        | 설명                   |
| ------------------------------------------ | -------------------- |
| `processed/merged_symptoms.csv`            | 통합된 질병-증상 데이터 (정제됨)  |
| `processed/disease_symptom_map.csv`        | 질병 → 증상 리스트 매핑       |
| `processed/symptom_normalization_map.json` | 증상 정규화 맵 (오타/중복 대응용) |
| `processed/tfidf_vectors.npz`              | TF-IDF 벡터 데이터        |
| `processed/tfidf_feature_names.json`       | TF-IDF 피처 이름         |
