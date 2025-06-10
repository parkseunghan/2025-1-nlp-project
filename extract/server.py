from fastapi import FastAPI
from pydantic import BaseModel
import time

# 서비스 함수 import
from services.translator import translate_to_english
from services.symptom_service import extract_combined_symptoms
from services.llm_service import extract_symptoms_with_llm
from services.hybrid_service import extract_hybrid_symptoms

# 유틸
from utils.text_cleaner import clean_text

# 요청 모델
class TextRequest(BaseModel):
    text: str

# FastAPI 인스턴스
app = FastAPI()

# ----------------------------
# ✅ NLP 기반 증상 추출 API
# ----------------------------
@app.post("/extract")
async def extract_nlp_symptoms(request: TextRequest):
    original_text = request.text
    cleaned_text = clean_text(original_text)
    translated = translate_to_english(cleaned_text)
    results = extract_combined_symptoms(cleaned_text, translated)

    return {
        "original": original_text,
        "cleaned": cleaned_text,
        "translated": translated,
        "results": results,
    }

# ----------------------------
# ✅ LLM 기반 증상 추출 API
# ----------------------------
@app.post("/extract/llm")
async def extract_llm_symptoms(request: TextRequest):
    results = await extract_symptoms_with_llm(request.text)
    return {
        "original": request.text,
        "llm_results": results,
    }

# ----------------------------
# ✅ 하이브리드(NLP + LLM) 추출 API
# ----------------------------
@app.post("/extract/hybrid")
async def extract_hybrid_symptoms_api(request: TextRequest):
    start = time.time()
    results = await extract_hybrid_symptoms(request.text)
    elapsed = time.time() - start
    print(f"\n⏱️ 하이브리드 추출 소요 시간: {elapsed:.2f}초")
    return {
        "original": request.text,
        "hybrid_results": results,
    }

# ----------------------------
# ✅ 실행 (터미널 직접 실행 시)
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    # 윈도우 콘솔에서 한글 깨짐 방지
    if os.name == "nt":
        sys.stdout.reconfigure(encoding='utf-8')
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
