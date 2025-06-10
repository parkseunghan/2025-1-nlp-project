import json
from typing import List, Dict, Tuple, Set
import os

# 외부 JSON 기반 로딩
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_RULES_PATH = os.path.join(BASE_DIR, "data", "symptom_token_rules.json")

with open(TOKEN_RULES_PATH, "r", encoding="utf-8") as f:
    raw_rules = json.load(f)
    
SYMPTOM_RULES = {}
for rule in raw_rules:
    for en in rule.get("en", []):
        SYMPTOM_RULES[en.lower()] = rule["id"]


def normalize_symptom_id(symptom: str) -> str:
    return SYMPTOM_RULES.get(symptom.strip().lower(), symptom.strip().lower())

def is_known_symptom(symptom: str) -> bool:
    return symptom in SYMPTOM_RULES.values()


def deduplicate_results(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    symptom + time 조합이 중복되지 않도록 결과 리스트를 정제
    """
    seen: Set[Tuple[str, str]] = set()
    unique: List[Dict[str, str]] = []

    for item in results:
        normalized_symptom = normalize_symptom_id(item["symptom"])
        time = item.get("time")
        key = (normalized_symptom, time)

        if key not in seen:
            seen.add(key)
            unique.append({"symptom": normalized_symptom, "time": time})

    return unique
