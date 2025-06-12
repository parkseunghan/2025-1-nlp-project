import os
import json
import kss
import httpx
from datetime import datetime
from typing import List, Dict, Tuple, Set
from utils.hybrid_utils import normalize_symptom_id, is_known_symptom

# ✅ 설정
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"
UNKNOWN_LOG_PATH = "logs/unknown_symptom_log.json"

LLM_PROMPT_TEMPLATE = """You are a medical AI that specializes in extracting symptoms from user input.

Your task is to extract ONLY the medical symptoms explicitly mentioned in the following Korean sentence.
- DO NOT guess symptoms that are not clearly stated.
- DO NOT infer, translate, or explain.
- DO NOT include Korean.
- DO NOT add modifiers like (mild), (severe), etc.
- DO NOT include adjectives like "persistent", "chronic", or "frequent" in the symptom field. Instead, express them using the "time" field as "persistent".
Respond ONLY with a valid JSON array of objects.
Each object must include:
- "symptom": an English medical keyword (e.g., "fever", "cough", "abdominal pain")
- "time": "morning", "afternoon", "evening", "night", "persistent", or null

Valid Output:
[
  { "symptom": "fever", "time": "night" },
  { "symptom": "headache", "time": null },
  { "symptom": "cough", "time": "persistent" }
]

Now extract symptoms from this sentence:
"{sentence}"
"""


def save_unknown_symptom_to_file(symptom: str, sentence: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {"datetime": now, "sentence": sentence.strip()}

    os.makedirs(os.path.dirname(UNKNOWN_LOG_PATH), exist_ok=True)

    if os.path.exists(UNKNOWN_LOG_PATH):
        with open(UNKNOWN_LOG_PATH, "r", encoding="utf-8") as f:
            log_data = json.load(f)
    else:
        log_data = {}

    if symptom not in log_data:
        log_data[symptom] = [new_entry]
    else:
        if new_entry not in log_data[symptom]:
            log_data[symptom].append(new_entry)

    with open(UNKNOWN_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)


def split_korean_sentences(text: str) -> List[str]:
    return kss.split_sentences(text)



async def extract_llm_only_symptoms(text: str) -> List[Dict[str, str]]:
    print("=" * 60)
    print(f"🧾 입력 문장: {text}")

    sentences = split_korean_sentences(text)
    print(f"✂️ 분리된 문장 수: {len(sentences)}")

    all_results: List[Dict[str, str]] = []
    seen: Set[Tuple[str, str]] = set()

    async with httpx.AsyncClient() as client:
        for idx, sentence in enumerate(sentences, 1):
            prompt = LLM_PROMPT_TEMPLATE.replace("{sentence}", sentence.strip())
            print(f"\n🧠 [문장 {idx}] '{sentence.strip()}'")

            parsed = []
            retry_count = 0
            max_retries = 2

            while retry_count <= max_retries and not parsed:
                try:
                    response = await client.post(
                        OLLAMA_URL,
                        json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
                        timeout=30.0
                    )
                    response.raise_for_status()
                    raw = response.text.strip()
                    print(f"📩 LLM 응답 원문 (시도 {retry_count+1}):\n{raw}")

                    output = response.json().get("response", "").strip()
                    parsed = json.loads(output) if output.startswith("[") else []

                except Exception as e:
                    print(f"❌ LLM 처리 실패 (시도 {retry_count+1}): {e}")
                    parsed = []  # 실패했을 경우 비우기

                retry_count += 1

            # ✅ 최종 파싱 성공 시 처리
            for item in parsed:
                raw_symptom = item.get("symptom")
                time = item.get("time")

                if not isinstance(raw_symptom, str):  # 문자열이 아닐 경우 건너뜀
                    print(f"⚠️ 무시된 잘못된 symptom 항목: {item}")
                    continue

                sid = normalize_symptom_id(raw_symptom)
                key = (sid, time)

                if key not in seen:
                    seen.add(key)

                    if is_known_symptom(sid):
                        all_results.append({"symptom": sid, "time": time})
                    else:
                        save_unknown_symptom_to_file(sid, sentence)


    print("\n------------------------------------------------------------")
    print("🩺 최종 증상 추출 결과:")
    for r in all_results:
        print(f"   - {r['symptom']} (time: {r['time']})")
    print("=" * 60)

    return all_results
