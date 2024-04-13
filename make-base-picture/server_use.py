from kiwi import sbg_noun_extractor
from lexical_relationship_analysis import lex_rel_anal
from translation import translate_text_list
from karlo import make_prompt, t2i, show_pic
import time
import json

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
with open('make-base-picture/base-picture/base-picture-labeling.json', 'r', encoding='utf-8') as f:
    label_data = json.load(f)
true_words = set()
false_words = set()

for data in label_data:
    if data["picture"] == thema:
        label = set(data["keywords"])
        break

for user_keyword in results:
    found_word = False
    for base_keyword in label:
        print(user_keyword,"와 ",base_keyword,"를 비교하겠습니다.") #새, 꽃, 강, 나무, 산, 구름, 길
        similarity_result, similarity_score = lex_rel_anal(user_keyword, base_keyword)
        if similarity_result:
            true_words.add(base_keyword)
            found_word = True
    if not found_word:
        false_words.add(user_keyword)

print("정답 단어:", true_words) #정답일 경우 프롬프트 그대로 출력 -> 키워드와 프롬프트 문장 간 연결 필요
print("오답 단어:", false_words)
print("전체 키워드 개수:", len(label))
print("정답 키워드 개수:", len(true_words))
# 두 세트 합쳐서 5번 그림 생성에 넣기


#4 영어로 번역
true_words = translate_text_list(false_words)
print(f"번역한 문장: {false_words}")
time_check(start)

#5 그림 생성
prompt = make_prompt(thema, true_words)
print(f"생성한 프롬프트: {prompt}")

response = t2i(prompt)
time_check(start)

show_pic(response)
