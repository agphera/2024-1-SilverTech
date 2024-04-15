# 1. pip install google-cloud-translate==2.0.1
# 2. 수채 프로젝트에 추가 (call me)
# 3. [Cloud CLI 설치] https://cloud.google.com/sdk/docs/install?hl=ko <= 인증키 사용하기 위해 사용
# 4. 설치 후 터미널에서 gcloud auth application-default login 실행 https://cloud.google.com/docs/authentication/api-keys?hl=ko#using-with-client-libs
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

    if isinstance(text, bytes):
        text = text.decode("utf-8")
    
    results = []
    with ThreadPoolExecutor() as executor:
        future_to_text = {executor.submit(translate_text_single, te, translate_client): te for te in text}
        for future in as_completed(future_to_text):
            results.append(future.result())
    
    return results

if __name__ == "__main__":
    print(translate_text_list(['배', '바다', '돛', '선장']))
    print(translate_text_list(['배', '사과', '나무', '산']))