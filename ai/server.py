from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from scripts.predict_disease import predict_disease

app = FastAPI()

# ✅ 증상 항목 정의 (symptom + time)
class SymptomItem(BaseModel):
    symptom: str
    time: Optional[str] = None  # 시간 정보는 선택사항

# ✅ 요청 본문 모델 정의
class SymptomsRequest(BaseModel):
    symptoms: List[SymptomItem]

# ✅ 예측 엔드포인트
@app.post("/predict")
async def predict_endpoint(req: SymptomsRequest):
    try:
        # 🔍 실제 예측에 사용할 symptom name만 추출
        symptom_names = [s.symptom for s in req.symptoms]

        # 🧠 예측 수행
        result = predict_disease(symptom_names)

        # 🖨️ 콘솔 출력
        from pprint import pprint
        print("\n✅ 예측 결과 (전체 필드 출력):")
        pprint(result, indent=2, width=100)

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ 로컬에서 직접 실행할 경우
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8002, reload=True)
