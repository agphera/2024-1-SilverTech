from function.kiwi import sbg_noun_extractor
from function.lexical_relationship_analysis import user_base_similarity
from function.translation import translate_text_list
from function.karlo import make_prompt, t2i, show_pic
import time

def level_choose(data):
    #if 사용자정보 x -> level = 1
    #else level=user_level
    #level 에 따른 그림 분류해놓고 thema = level1[0]
    pass


def scoring_points(data):
    #1 한국어 문장 입력
    INPUT_TEXT = data
    THEMA = thema
    print(f"입력 받은 문장: {INPUT_TEXT}")


    #2 명사(키워드) 추출
    results = sbg_noun_extractor(INPUT_TEXT)
    print(f"키워드: {results}")


    #3 유사도 측정으로 점수 결정
    true_word, false_word, accuracy, whole_prompt_word = user_base_similarity(THEMA, results)
    print("정답 키워드 개수:", len(true_word)) 
    print("정답 단어:", true_word)
    print("정답률:", accuracy)
    print("오답 단어:", false_word)


    #4 영어로 번역
    false_word_trans = translate_text_list(false_word) #틀린 단어만 번역
    print(f"번역한 오답 단어: {false_word_trans}")

    #5 프롬프트에 들어갈 전체 단어 모음
    whole_prompt_word = whole_prompt_word.union(false_word_trans)

    return accuracy, true_word, whole_prompt_word

# def scoring_points(data, thema):
#     #1 STT 데이터와 그림 주제 저장
#     INPUT_TEXT = data
#     THEMA = thema

#     #2 명사(키워드) 추출
#     results = sbg_noun_extractor(INPUT_TEXT)

#     #3 유사도 측정으로 점수 결정
#     true_word, false_word, accuracy, whole_prompt_word = user_base_similarity(THEMA, results)

#     #4 영어로 번역
#     false_word_trans = translate_text_list(false_word) #틀린 단어만 번역

#     #5 프롬프트에 들어갈 전체 단어 모음
#     whole_prompt_word = whole_prompt_word.union(false_word_trans)

#     return accuracy, true_word, whole_prompt_word


def make_picture(whole_prompt_word):
    THEMA = "park1"
    
    #1 프롬프트 생성
    print(whole_prompt_word)
    prompt = make_prompt(THEMA, list(whole_prompt_word))
    print(f"생성한 프롬프트: {prompt}")

    #2 그림 생성
    response = t2i(prompt)
    print(response)

    return response