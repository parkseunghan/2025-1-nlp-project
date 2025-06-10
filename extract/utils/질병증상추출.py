import json

# 파일 경로
disease_file = "./data/disease_label_map.json"
symptom_file = "./data/symptom_label_map.json"

# id만 추출하는 함수
def extract_ids(file_path):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    return [item["id"] for item in data]

# id 리스트 추출
disease_ids = extract_ids(disease_file)
symptom_ids = extract_ids(symptom_file)

# 파일 저장 함수
def save_to_file(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 저장
save_to_file(disease_ids, "./outputs/disease_ids.json")
save_to_file(symptom_ids, "./outputs/symptom_ids.json")

print("✅ id 저장 완료: disease_ids.json, symptom_ids.json")
