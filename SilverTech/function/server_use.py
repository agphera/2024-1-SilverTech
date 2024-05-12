from function.kiwi import sbg_noun_extractor
from function.lexical_relationship_analysis import user_base_similarity
from function.translation import translate_text_list
from function.karlo import make_prompt, t2i, show_pic
import json

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
    true_word, translate_word, accuracy, whole_prompt_word = user_base_similarity(THEMA, results)
    print("정답 키워드 개수:", len(true_word)) 
    print("정답 단어:", true_word)
    print("정답률:", accuracy)
    print("번역할 단어:", translate_word)


    if accuracy >= 0.99: 
        # 정확도가 100%인 경우 base 그림과 동일한 프롬프트로 만듦
        with open('../make-base-picture/base-picture/base-picture-labeling.json', 'r', encoding='utf-8') as f:
            label_data = json.load(f)

        for data in label_data:
            if data["picture"] == THEMA:
                label_prompt = data["prompt"] # 새: english, 꽃: english, 강: english
                break
        whole_prompt_word = label_prompt.values()

    else:
        #4 영어로 번역
        word_trans = translate_text_list(translate_word) # 부가적인 정답 키워드 및 틀린 키워드 번역
        print(f"번역한 단어: {word_trans}")

        #5 프롬프트에 들어갈 전체 단어 모음
        whole_prompt_word = whole_prompt_word.union(word_trans)

    return accuracy, true_word, whole_prompt_word

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
