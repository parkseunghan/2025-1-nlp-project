import re
from typing import List
from utils.korean_rules import JOSA, EOMI, COMPOSITE_BODY_PARTS

STOPWORDS = {"너무", "좀", "정말", "약간", "그리고", "또는", "그래서"}


def clean_text(text: str) -> str:
    return re.sub(r"[^\w\sㄱ-힣]", "", text).strip().lower()

def remove_josa_and_eomi(token: str) -> str:
    while True:
        original = token
        for j in sorted(JOSA, key=len, reverse=True):
            if token.endswith(j):
                token = token[: -len(j)]
                break
        for e in sorted(EOMI, key=len, reverse=True):
            if token.endswith(e):
                token = token[: -len(e)]
                break
        if token == original:
            break
    return token

def expand_composite_parts(tokens: List[str]) -> List[str]:
    expanded = []
    for token in tokens:
        if token in COMPOSITE_BODY_PARTS:
            expanded.extend(COMPOSITE_BODY_PARTS[token])
        else:
            expanded.append(token)
    return expanded

def clean_and_tokenize(text: str) -> List[str]:
    cleaned = clean_text(text)
    raw_tokens = cleaned.split()
    whitelist = {"배", "피", "열", "목", "속", "눈", "귀", "코", "팔", "위", "몸", "입", "손", "발", "다리"}

    tokens = []
    for token in raw_tokens:
        core = remove_josa_and_eomi(token)
        if (len(core) > 1 or core in whitelist) and core not in STOPWORDS:
            tokens.append(core)

    expanded = expand_composite_parts(tokens)
    return expanded
