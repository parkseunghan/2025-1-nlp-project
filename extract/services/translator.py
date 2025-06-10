from googletrans import Translator

translator = Translator()

def translate_to_english(text: str) -> str:
    try:
        result = translator.translate(text, src="ko", dest="en")
        return result.text
    except Exception:
        return text  # 번역 실패 시 원문 그대로 반환
