from karlo import make_prompt, t2i, show_pic
from translation import translate_text_list
from kiwi import sbg_noun_extractor


#1 한국어 문장 입력
text = "새가 날아다니고 꽃이 피어있네 옷을 길이 보이고 넘어예는 호수도 있구나 여러 나무들이 다양한 색으로 입을 펼쳤고 멀리 희미하게 산이 보이려 하네"
print(f"입력 받은 문장: {text}\n")

#2 키워드 추출
results = sbg_noun_extractor(text)
print(f"키워드: {results}\n")

#3 유사도 측정으로 점수 결정


#4 영어로 번역
results = translate_text_list(results)
print(f"번역한 문장: {results}\n")

#5 그림 생성
prompt = make_prompt("park1", results)
print(f"생성한 프롬프트: {prompt}")

response = t2i(prompt)
show_pic(response)