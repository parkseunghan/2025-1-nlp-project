from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from scripts.predict_disease import predict_disease

app = FastAPI()

class SymptomsRequest(BaseModel):
    symptoms: List[str]

@app.post("/predict")
async def predict_endpoint(req: SymptomsRequest):
    try:
        result = predict_disease(req.symptoms)

        # ✅ 콘솔 출력
        from pprint import pprint
        print("\n✅ 예측 결과 (전체 필드 출력):")
        pprint(result, indent=2, width=100)

        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ✅ 직접 실행 시에만 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8002, reload=True)
