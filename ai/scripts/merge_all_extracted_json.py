import json
from pathlib import Path

# ✅ 입력 파일 목록
json_paths = [
    Path("outputs/karthik_extracted.json"),
    Path("outputs/kaushi268_extracted.json"),
    Path("outputs/laksika_extracted.json"),
    Path("outputs/pranay_extracted.json"),
]

# ✅ 초기 통합 구조
merged_data = {
    "diseases": set(),
    "symptoms": set()
}

# ✅ 파일별 병합
for path in json_paths:
    if not path.exists():
        print(f"❗ 파일이 존재하지 않음: {path}")
        continue

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    merged_data["diseases"].update(data.get("diseases", []))
    merged_data["symptoms"].update(data.get("symptoms", []))

# ✅ 정렬 및 리스트로 변환
merged_data["diseases"] = sorted(merged_data["diseases"])
merged_data["symptoms"] = sorted(merged_data["symptoms"])

# ✅ 저장
output_path = Path("outputs/merged_extracted.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=2, ensure_ascii=False)

print(f"✅ 통합 JSON 생성 완료 → {output_path}")
print(f"🦠 질병 수: {len(merged_data['diseases'])}개")
print(f"🤒 증상 수: {len(merged_data['symptoms'])}개")
