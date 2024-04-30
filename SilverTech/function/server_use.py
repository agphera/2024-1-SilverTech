from function.kiwi import sbg_noun_extractor
from function.lexical_relationship_analysis import user_base_similarity
from function.translation import translate_text_list
from function.karlo import make_prompt, t2i, show_pic
import time

def scoring_points(data):
    #1 한국어 문장 입력
    INPUT_TEXT = data
    THEMA = "park1"
    print(f"입력 받은 문장: {INPUT_TEXT}")


    #2 키워드 추출
    results = sbg_noun_extractor(INPUT_TEXT)
    print(f"키워드: {results}")


    #3 유사도 측정으로 점수 결정
    true_word, false_word, accuracy, whole_prompt = user_base_similarity(THEMA, results)
    print("정답 키워드 개수:", len(true_word)) 
    print("정답 단어:", true_word)
    print("정답률:", accuracy)
    print("오답 단어:", false_word)


    #4 영어로 번역
    false_word_trans = translate_text_list(false_word) #틀린 단어만 번역
    print(f"번역한 오답 단어: {false_word_trans}")
    whole_prompt = whole_prompt.union(false_word_trans)

    return accuracy, true_word, whole_prompt

def make_picture(whole_prompt):
    THEMA = "park1"
    
    #5 그림 생성
    print(whole_prompt)
    prompt = make_prompt(THEMA, list(whole_prompt))
    print(f"생성한 프롬프트: {prompt}")

    response = t2i(prompt)
    print(response)

    return response
