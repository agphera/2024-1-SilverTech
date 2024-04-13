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
true_word = set()
false_word = set()
whole_prompt = set()

for data in label_data:
    if data["picture"] == thema:
        label_keyword = set(data["keywords"])
        label_prompt = data["prompt"]
        break

for user_keyword in results:
    found_word = False
    for base_keyword in label_keyword:
        print(user_keyword,"와 ",base_keyword,"를 비교하겠습니다.") #새, 꽃, 강, 나무, 산, 구름, 길
        similarity_result, similarity_score = lex_rel_anal(user_keyword, base_keyword)
        if similarity_result:
            found_word = True
            true_word.add(base_keyword)
            if base_keyword in label_prompt:
                whole_prompt.add(label_prompt[base_keyword])
            break
    if not found_word:
        false_word.add(user_keyword)

print("정답 단어:", true_word)
print("오답 단어:", false_word)
print("전체 키워드 개수:", len(label_keyword))
print("정답 키워드 개수:", len(true_word))


#4 영어로 번역
false_word_trans = translate_text_list(false_word) #틀린 단어만 번역
print(f"번역한 문장: {false_word_trans}")
whole_prompt = whole_prompt.union(false_word_trans)
time_check(start)


#5 그림 생성
print(whole_prompt)
prompt = make_prompt(thema, list(whole_prompt))
print(f"생성한 프롬프트: {prompt}")

response = t2i(prompt)
time_check(start)

show_pic(response)
