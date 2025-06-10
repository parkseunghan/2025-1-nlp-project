from typing import List, Dict, Optional
from utils.symptom_mapping import SYMPTOM_MAPPING
from utils.text_cleaner import clean_and_tokenize

TIME_KEYWORDS = {
    "ko": {
        "아침": "morning", "오전": "morning", "점심": "afternoon",
        "오후": "afternoon", "저녁": "evening", "밤": "night",
    },
    "en": {
        "morning": "morning", "afternoon": "afternoon",
        "evening": "evening", "night": "night",
    },
}

def extract_combined_symptoms(text_ko: str, text_en: str, verbose: bool = False) -> List[Dict[str, str]]:
    if verbose:
        print(f"\n🧾 [Step 1] 원문(ko): {text_ko}")
        print(f"🔵 [Step 2] 번역(en): {text_en}")
    
    results = []
    tokens_ko = clean_and_tokenize(text_ko)
    tokens_en = clean_and_tokenize(text_en.lower())

    if verbose:
        print(f"\n🟡 [Step 3] Tokenized (ko): {tokens_ko}")
        print(f"🟡 [Step 4] Tokenized (en): {tokens_en}")
        print(f"🟡 [Step 4-1] 정제 후 토큰 (ko): {tokens_ko}")
        print(f"🟡 [Step 4-2] 정제 후 토큰 (en): {tokens_en}")

    for symptom, mapping in SYMPTOM_MAPPING.items():
        if any(keyword in text_ko for keyword in mapping["ko"]):
            if verbose:
                print(f"✅ [KO match] '{symptom}' matched by keyword in: {mapping['ko']}")
            results.append({"symptom": symptom, "time": detect_time(text_ko, "ko")})
            continue

        if any(keyword in text_en for keyword in mapping["en"]):
            if verbose:
                print(f"✅ [EN match] '{symptom}' matched by keyword in: {mapping['en']}")
            results.append({"symptom": symptom, "time": detect_time(text_en, "en")})
            continue

        for token_set in mapping.get("token_sets", []):
            part1_match = [tok for tok in tokens_ko if tok in token_set["part1"]]
            part2_match = [tok for tok in tokens_ko if tok in token_set["part2"]]
            if verbose:
                print(f"🔍 [DEBUG] {symptom} token_sets 검사 - part1: {part1_match}, part2: {part2_match}")
            if part1_match and part2_match:
                if verbose:
                    print(f"✅ [TokenSet match] '{symptom}' matched by part1: {part1_match}, part2: {part2_match}")
                results.append({"symptom": symptom, "time": detect_time(text_ko, "ko")})
                break

    composite = handle_composite_symptoms(text_ko, results)
    if composite:
        if verbose:
            print(f"✅ [Composite] Added symptoms from '몸살': {[s['symptom'] for s in composite]}")
        results += composite

    final = deduplicate_results(results)
    if verbose:
        print(f"\n🟢 [Step 5] 최종 추출 결과: {final}")
    return final


def detect_time(text: str, lang: str) -> Optional[str]:
    return next((v for k, v in TIME_KEYWORDS[lang].items() if k in text), None)

def deduplicate_results(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen, unique = set(), []
    for item in results:
        key = (item["symptom"], item["time"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

def handle_composite_symptoms(text_ko: str, existing_results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    composite_symptoms = []
    if "몸살" in text_ko:
        # 몸살로 유발되는 증상 표현
        related_ko_keywords = ["오한", "근육통", "피로", "열"]

        for keyword in related_ko_keywords:
            matched_id = None
            for sid, mapping in SYMPTOM_MAPPING.items():
                if keyword in mapping["ko"]:
                    matched_id = sid
                    break

            if matched_id and not any(r["symptom"] == matched_id for r in existing_results):
                composite_symptoms.append({
                    "symptom": matched_id,
                    "time": detect_time(text_ko, "ko")
                })

    return composite_symptoms
