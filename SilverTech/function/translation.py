from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import translate_v2 as translate

def translate_text_single(te, translate_client):
    """단일 텍스트를 번역합니다."""
    return translate_client.translate(te, target_language="en")["translatedText"]

def translate_text_list(text: list) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.Client()

    results = []
    with ThreadPoolExecutor() as executor:
        future_to_text = {executor.submit(translate_text_single, te, translate_client): te for te in text}
        for future in as_completed(future_to_text):
            results.append(future.result())
    
    return results

def translate_text_single(te, translate_client):
    return translate_client.translate(te, target_language="en")["translatedText"] # API 호출

def translate_text_list(text: list) -> dict:
    translate_client = translate.Client()

    results = []
    with ThreadPoolExecutor() as executor: # 멀티스레딩을 사용해 병렬적으로 API 호출
        future_to_text = {executor.submit(translate_text_single, te, translate_client): te for te in text}
        for future in as_completed(future_to_text):
            results.append(future.result())
    
    return results # 번역된 결과 반환