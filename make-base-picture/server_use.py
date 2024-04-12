from karlo import make_prompt, t2i, show_pic
from translation import translate_text_list
from kiwi import sbg_noun_extractor
import time

def time_check(start):
    current = time.time()
    print(f"소요된 시간: {current-start} sec\n")

start = time.time()

#1 한국어 문장 입력: park1에 대한 설명을 음성 녹음 -> 한글 변환한 텍스트임. (조용한 환경에서 진행함)
text = "새가 날아다니고 꽃이 피어있네 옷을 길이 보이고 넘어예는 호수도 있구나 여러 나무들이 다양한 색으로 입을 펼쳤고 멀리 희미하게 산이 보이려 하네"
thema = "park1"
print(f"입력 받은 문장: {text}")
time_check(start)

#2 키워드 추출
results = sbg_noun_extractor(text)
print(f"키워드: {results}")
time_check(start)

#3 유사도 측정으로 점수 결정
## step 1.
### a. (정의) 키워드 최종 검수. 변경사항은 공유해서 마무리
### b. (정의) 키워드: 영어 -> 한글

## step 2.
### a. 사용자 키워드와, base 그림 키워드 비교하면서 맞는 키워드 체크(API)
### b. 맞는 키워드는 기존 영어 사용, 틀린 키워드는 영어로 번역 => 그림 생성
### c. 정답률 표현

#4 영어로 번역
results = translate_text_list(results)
print(f"번역한 문장: {results}")
time_check(start)

#5 그림 생성
prompt = make_prompt(thema, results)
print(f"생성한 프롬프트: {prompt}")

response = t2i(prompt)
time_check(start)

show_pic(response)
