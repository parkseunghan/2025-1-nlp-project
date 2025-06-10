import json

# 파일 불러오기
with open("outputs/symptoms.json", "r") as f:
    symptoms = set(json.load(f))

with open("outputs/symptom_ids.json", "r") as f:
    symptom_ids = set(json.load(f))

# 서로 중복되지 않는 단어 찾기
only_in_symptoms = sorted(list(symptoms - symptom_ids))
only_in_symptom_ids = sorted(list(symptom_ids - symptoms))

# 결과 출력
print("✅ symptoms에만 있는 증상:", only_in_symptoms)
print("✅ symptom_ids에만 있는 증상:", only_in_symptom_ids)

# 결과 저장
with open("only_in_symptoms.json", "w") as f:
    json.dump(only_in_symptoms, f, indent=2)

with open("only_in_symptom_ids.json", "w") as f:
    json.dump(only_in_symptom_ids, f, indent=2)
