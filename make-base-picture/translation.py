# pip install google-cloud-translate==2.0.1
# [Cloud CLI 설치] https://cloud.google.com/sdk/docs/install?hl=ko <= 일단 인증키 받기 위해서 다운 받았음. 나만 필요한건지 모르겠네


def translate_text_list(text: list) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")
    
    text = ' '.join(text)
    results = translate_client.translate(text, target_language="en")["translatedText"]
    results = results.split(' ')
    results = [word[0].lower() + word[1:] for word in results]    
    # results = []
    # for te in text: 
    #     results.append(translate_client.translate(te, target_language="en")["translatedText"])

    return results

if __name__ == "__main__":
    print(translate_text_list(['배', '바다', '돛', '선장']))
    print(translate_text_list(['배', '사과', '나무', '산']))