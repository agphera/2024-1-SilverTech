# 1. pip install google-cloud-translate==2.0.1
# 2. 수채 프로젝트에 추가 (call me)
# 3. [Cloud CLI 설치] https://cloud.google.com/sdk/docs/install?hl=ko <= 인증키 사용하기 위해 사용
# 4. 설치 후 터미널에서 gcloud auth application-default login 실행 https://cloud.google.com/docs/authentication/api-keys?hl=ko#using-with-client-libs


def translate_text_list(text: list) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")
    
    # text = ' '.join(text)
    # results = translate_client.translate(text, target_language="en")["translatedText"]
    # results = results.split(' ')
    # results = [word[0].lower() + word[1:] for word in results]    
    results = []
    for te in text: 
        results.append(translate_client.translate(te, target_language="en")["translatedText"])

    return results

if __name__ == "__main__":
    print(translate_text_list(['배', '바다', '돛', '선장']))
    print(translate_text_list(['배', '사과', '나무', '산']))