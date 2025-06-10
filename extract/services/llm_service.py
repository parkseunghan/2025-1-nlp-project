import kss
import httpx
import json
from typing import List, Dict, Set, Tuple
from utils.hybrid_utils import normalize_symptom_id, is_known_symptom

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

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


# ✅ 미정의 증상 로그 (전역 저장소)
unknown_symptom_log: Dict[str, Set[str]] = {}

def split_korean_sentences(text: str) -> List[str]:
    return kss.split_sentences(text)


async def extract_single_sentence_with_llm(sentence: str) -> List[Dict[str, str]]:
    prompt = LLM_PROMPT_TEMPLATE.replace("{sentence}", sentence.strip())

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30.0
            )
            response.raise_for_status()
            raw = response.text.strip()
            print(f"📩 LLM 응답 원문:\n{raw}")

            output = response.json().get("response", "").strip()
            parsed = json.loads(output) if output.startswith("[") else []

            # ✅ 미정의 증상 기록
            for item in parsed:
                symptom = item.get("symptom")
                norm = normalize_symptom_id(symptom)
                if not is_known_symptom(norm):
                    if norm not in unknown_symptom_log:
                        unknown_symptom_log[norm] = set()
                    unknown_symptom_log[norm].add(sentence.strip())

            return parsed

        except Exception as e:
            print(f"⚠️ LLM JSON 파싱 실패: {e}")
            return []


async def extract_symptoms_with_llm(text: str) -> List[Dict[str, str]]:
    sentences = split_korean_sentences(text)
    all_results: List[Dict[str, str]] = []
    seen = set()

    print("\n" + "=" * 60)
    print(f"🧾 입력 문장: {text}")
    print(f"✂️ 분리된 문장 수: {len(sentences)}")

    async with httpx.AsyncClient() as client:
        for idx, sentence in enumerate(sentences, 1):
            prompt = LLM_PROMPT_TEMPLATE.replace("{sentence}", sentence.strip())
            print(f"\n🧠 [문장 {idx}] '{sentence.strip()}'")

            try:
                response = await client.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL_NAME,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                response.raise_for_status()

                raw = response.text.strip()
                print(f"📩 LLM 응답 원문:\n{raw}")

                output = response.json().get("response", "").strip()
                parsed = json.loads(output) if output.startswith("[") else []

                # ✅ 미정의 증상 기록
                for item in parsed:
                    symptom = item.get("symptom")
                    norm = normalize_symptom_id(symptom)
                    if not is_known_symptom(norm):
                        if norm not in unknown_symptom_log:
                            unknown_symptom_log[norm] = set()
                        unknown_symptom_log[norm].add(sentence.strip())

                    key = (symptom, item.get("time"))
                    if key not in seen:
                        seen.add(key)
                        all_results.append(item)

            except Exception as e:
                print(f"❌ LLM 처리 실패: {e}")

    print("\n" + "-" * 60)
    print("🩺 최종 통합 증상 추출 결과:")
    for result in all_results:
        print(f"   - {result['symptom']} (time: {result['time']})")
    print("=" * 60)

    return all_results


# ✅ 새로운 미정의 증상 로그 조회용 함수 (외부 모듈에서 접근 가능)
def get_unknown_symptom_log() -> Dict[str, List[str]]:
    return {k: list(v) for k, v in unknown_symptom_log.items()}