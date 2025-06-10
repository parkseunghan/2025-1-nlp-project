import json
import os
from typing import Dict

def load_symptom_rules(json_path: str = "data/symptom_token_rules.json") -> Dict[str, dict]:
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ 파일이 존재하지 않음: {json_path}")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    symptom_mapping = {
        item["id"]: {
            "ko": item.get("ko", []),
            "en": item.get("en", []),
            "token_sets": item.get("token_sets", [])
        } for item in data
    }
    return symptom_mapping

SYMPTOM_MAPPING = load_symptom_rules()
