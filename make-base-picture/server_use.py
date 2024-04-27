from kiwi import sbg_noun_extractor
from lexical_relationship_analysis import user_base_similarity
from translation import translate_text_list
from karlo import make_prompt, t2i, show_pic
import time

def time_check(start):
    current = time.time()
    print(f"소요된 시간: {current-start} sec\n")

start = time.time()


# #1 한국어 문장 입력: park1에 대한 설명을 음성 녹음 -> 한글 변환한 텍스트임. (조용한 환경에서 진행함)
INPUT_TEXT = "새가 날아 다니고 호수 각 보여요 푸르른 나무와 화려한 꽃들이 많이 있어요"
THEMA = "park1"
print(f"입력 받은 문장: {INPUT_TEXT}")
time_check(start)


#2 키워드 추출
results = sbg_noun_extractor(INPUT_TEXT)
print(f"키워드: {results}")
time_check(start)


#3 유사도 측정으로 점수 결정
true_word, false_word, accuracy, whole_prompt = user_base_similarity(THEMA, results)
print("정답 키워드 개수:", len(true_word)) 
print("정답 단어:", true_word)
print("정답률:", accuracy)
print("오답 단어:", false_word)
time_check(start)


#4 영어로 번역
false_word_trans = translate_text_list(false_word) #틀린 단어만 번역
print(f"번역한 오답 단어: {false_word_trans}")
whole_prompt = whole_prompt.union(false_word_trans)
time_check(start)


#5 그림 생성
print(whole_prompt)
prompt = make_prompt(THEMA, list(whole_prompt))
print(f"생성한 프롬프트: {prompt}")

response = t2i(prompt)
time_check(start)

show_pic(response)
