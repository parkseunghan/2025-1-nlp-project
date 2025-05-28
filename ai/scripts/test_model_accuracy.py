# 📄 test_model_accuracy.py
import json
from predict_disease import predict_disease

# ✅ 질병-증상 매핑 파일 로딩
with open("data/disease_symptom_mapping.json", encoding="utf-8") as f:
    disease_symptom_map = json.load(f)

# ✅ 평가 통계
total = len(disease_symptom_map)
top1_correct = 0
top3_correct = 0

# ✅ 평가 수행
for disease, symptoms in disease_symptom_map.items():
    result = predict_disease(symptoms)
    top1 = result["fineLabel"]
    top3 = [r["fineLabel"] for r in result["ranks"]]

    if disease == top1:
        top1_correct += 1
    if disease in top3:
        top3_correct += 1

    print(f"🎯 정답: {disease} | ✅ Top-1: {top1} | {'🟢' if disease in top3 else '🔴'} Top-3")

# ✅ 최종 결과 출력
print("\n📊 평가 결과")
print(f"총 질병 수: {total}")
print(f"Top-1 정확도: {top1_correct}/{total} = {top1_correct/total:.2%}")
print(f"Top-3 정확도: {top3_correct}/{total} = {top3_correct/total:.2%}")
