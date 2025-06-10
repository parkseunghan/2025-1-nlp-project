import json

# JSON 파일 불러오기
with open("data/disease_symptom_mapping.json", "r") as f:
    data = json.load(f)

# 질병 목록 추출
diseases = list(data.keys())

# 증상 목록 추출 (중복 제거 후 정렬)
symptoms = sorted(set(symptom for symptom_list in data.values() for symptom in symptom_list))

# JSON 파일로 저장
with open("data/diseases.json", "w") as f:
    json.dump(diseases, f, indent=2)

with open("data/symptoms.json", "w") as f:
    json.dump(symptoms, f, indent=2)
