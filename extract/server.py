from fastapi import FastAPI

from pydantic import BaseModel
import time

# 서비스 함수 import
from services.translator import translate_to_english
from services.symptom_service import extract_combined_symptoms
from services.hybrid_service import extract_hybrid_symptoms
from services.llm_only_service import extract_llm_only_symptoms

# 유틸
from utils.text_cleaner import clean_text

from fastapi.responses import JSONResponse
import json
import os

# FastAPI 인스턴스
app = FastAPI()

LOG_FILE = "logs/unknown_symptom_log.json"  # 경로 수정 가능

@app.get("/logs/unknown-symptoms")
def get_unknown_symptoms():
    log_file = "logs/unknown_symptom_log.json"
    if not os.path.exists(log_file):
        return JSONResponse(content={"message": "Log file not found"}, status_code=404)

    with open(log_file, "r", encoding="utf-8") as f:
        raw_log = json.load(f)

    cleaned_log = {}
    for label, entries in raw_log.items():
        seen_sentences = {}
        for entry in entries:
            sentence = entry["sentence"]
            dt = entry["datetime"]
            if sentence not in seen_sentences or dt < seen_sentences[sentence]["datetime"]:
                seen_sentences[sentence] = entry
        cleaned_log[label] = list(seen_sentences.values())

    return cleaned_log

# 요청 모델
class TextRequest(BaseModel):
    text: str





# ----------------------------
# ✅ NLP 기반 증상 추출 API
# ----------------------------
@app.post("/extract/nlp")
async def extract_nlp_symptoms(request: TextRequest):
    original_text = request.text
    cleaned_text = clean_text(original_text)
    translated = translate_to_english(cleaned_text)
    results = extract_combined_symptoms(cleaned_text, translated)

    return {
        "original": original_text,
        "symptoms": results,
    }


# ----------------------------
# ✅ LLM 기반 증상 추출 API (단독 모델 사용)
# ----------------------------
@app.post("/extract/llm")
async def extract_llm_symptoms_api(request: TextRequest):
    results = await extract_llm_only_symptoms(request.text)
    return {"original": request.text, "symptoms": results}


# ----------------------------
# ✅ 하이브리드(NLP + LLM) 추출 API
# ----------------------------
@app.post("/extract/hybrid")
async def extract_hybrid_symptoms_api(request: TextRequest):
    start = time.time()
    results = await extract_hybrid_symptoms(request.text)
    elapsed = time.time() - start
    print(f"\n⏱️ 하이브리드 추출 소요 시간: {elapsed:.2f}초")
    return {"original": request.text, "symptoms": results}


# ----------------------------
# ✅ 실행 (터미널 직접 실행 시)
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    import sys
    import os

    # 윈도우 콘솔에서 한글 깨짐 방지
    if os.name == "nt":
        sys.stdout.reconfigure(encoding="utf-8")
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
