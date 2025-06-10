import asyncio
import os
import json
from datetime import datetime
from typing import List, Dict, Tuple, Set
from services.translator import translate_to_english
from services.llm_service import split_korean_sentences, extract_single_sentence_with_llm
from services.symptom_service import extract_combined_symptoms
from utils.hybrid_utils import normalize_symptom_id, is_known_symptom

UNKNOWN_LOG_PATH = "logs/unknown_symptom_log.json"


def extract_nlp_symptoms(text: str) -> List[Dict[str, str]]:
    """
    Rule 기반 증상 추출 (한국어 → 번역된 텍스트 활용)
    """
    cleaned = text.strip()
    translated = translate_to_english(cleaned)
    nlp_results = extract_combined_symptoms(cleaned, translated)
    print(f"\n🔎 NLP 추출 결과: {nlp_results}")
    return nlp_results


def save_unknown_symptoms_to_file(symptom: str, sentence: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {"datetime": now, "sentence": sentence.strip()}

    # 🧩 logs 디렉토리 없으면 생성
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



async def extract_llm_symptoms(text: str) -> List[Dict[str, str]]:
    """
    문장 분리 후 각 문장을 영어로 번역 → LLM에 병렬로 전달
    정의되지 않은 증상은 파일로 저장 (제외됨)
    """
    sentences_ko = split_korean_sentences(text)
    print(f"\n🧠 분리된 문장 수: {len(sentences_ko)}")

    tasks = []
    sentence_map = []
    for s in sentences_ko:
        s_clean = s.strip()
        s_translated = translate_to_english(s_clean)
        print(f"\n🧠 [문장] '{s_clean}' → 번역: '{s_translated}'")
        tasks.append(extract_single_sentence_with_llm(s_translated))
        sentence_map.append(s_clean)

    nested_results = await asyncio.gather(*tasks)
    all_results: List[Dict[str, str]] = []

    for idx, (orig_sentence, result) in enumerate(zip(sentence_map, nested_results), 1):
        print(f"\n📩 [LLM 응답 {idx}] for '{orig_sentence}':")
        print(result)
        for item in result:
            sid = normalize_symptom_id(item["symptom"])
            if is_known_symptom(sid):
                all_results.append({"symptom": sid, "time": item.get("time")})
            else:
                save_unknown_symptoms_to_file(sid, orig_sentence)

    return all_results


def merge_confidently(
    nlp_results: List[Dict[str, str]],
    llm_results: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    중복 제거 및 병합: NLP 우선, LLM은 보완
    """
    final: List[Dict[str, str]] = []
    seen: set[Tuple[str, str]] = set()

    for item in nlp_results:
        sid = normalize_symptom_id(item["symptom"])
        key = (sid, item.get("time"))
        seen.add(key)
        final.append({"symptom": sid, "time": item.get("time")})

    for item in llm_results:
        key = (item["symptom"], item.get("time"))
        if key not in seen:
            seen.add(key)
            final.append(item)

    return final


async def extract_hybrid_symptoms(text: str) -> List[Dict[str, str]]:
    print("=" * 60)
    print(f"🧾 입력 문장: {text}")

    # ✅ 병렬 실행 (NLP + LLM)
    nlp_task = asyncio.to_thread(extract_nlp_symptoms, text)
    llm_task = extract_llm_symptoms(text)
    nlp_results, llm_results = await asyncio.gather(nlp_task, llm_task)

    # ✅ 병합
    final_results = merge_confidently(nlp_results, llm_results)

    print("\n------------------------------------------------------------")
    print("🩺 최종 통합 증상 추출 결과:")
    for r in final_results:
        print(f"   - {r['symptom']} (time: {r['time']})")
    print("=" * 60)

    return final_results
