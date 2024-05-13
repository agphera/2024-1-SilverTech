import os
import urllib3
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# API 키 작성된 메모장 주소
keys_file_path = os.path.join('../API', 'api_keys.txt')

# 파일에서 API 키를 로드하는 함수
with open(keys_file_path, 'r', encoding='utf-8') as file:
    keys = json.load(file)

# API 키 사용
AI_API_KEY = f"{keys['ai_api_keys']}"


def lex_rel_anal(firstWord, secondWord):
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseWWN/WordRel"
    accessKey = AI_API_KEY
    
    # 1. API를 사용해 응답을 받아온다.
    # 1-1. 요청을 위한 준비 
    firstWord, firstSenseId = firstWord.split('_') if '_' in firstWord else (firstWord, None)
    secondWord, secondSenseId = secondWord.split('_') if '_' in secondWord else (secondWord, None)
    requestJson = { 
        "argument": {
            'first_word': firstWord,
            'first_sense_id': firstSenseId,
            'second_word': secondWord,
            'second_sense_id': secondSenseId
        }
    }
    http = urllib3.PoolManager()
    data = {}
    count = 0
    # 1-2. 요청 작업
    while 'return_object' not in data: # 올바른 응답이 오지 않은 경우 재요청
        if count >= 5:  # 5번 이상 정상적인 응답이 돌아오지 않는다면 False 반환하고 종료
            return (False, 0)
        
        response = http.request(
            "POST",
            openApiURL,
            headers={"Content-Type": "application/json; charset=UTF-8", "Authorization": accessKey},
            body=json.dumps(requestJson)
        )

        # JSON 데이터를 파이썬 딕셔너리로 변환
        data = json.loads(response.data)
        count += 1

    # 2. 유사도 측정 결과를 추출 
    similarities = data['return_object']['WWN WordRelInfo']['WordRelInfo']['Similarity']

    # 3. 특정 알고리즘의 score만 사용해 평균값을 구한다.
    average_score = 0
    for sim in similarities:
        if sim['Algorithm'] in ['ETRI', 'Resnik', 'Hirst and St-Onge', 'Pekar et al', 'Lin + GraSM']:
            average_score += sim['SimScore']
    average_score = average_score / 5
    return (True if average_score > 0.6 else False, average_score) 

def check_similarity_multithreading(user_keyword, base_keyword, delay):
    """
    lex_rel_anal 함수를 호출하고 결과를 반환하는 래퍼 함수.
    """
    time.sleep(delay)  # 대기 시간 적용
    similarity_result, average_score = lex_rel_anal(user_keyword, base_keyword)
    return similarity_result, average_score, base_keyword

def user_base_similarity(THEMA, results):
    with open('../make-base-picture/base-picture/base-picture-labeling.json', 'r', encoding='utf-8') as f:
        label_data = json.load(f)

    true_word = set() # 정답률 체크
    translate_word = set() # 번역용 단어
    whole_prompt_word = set() # 프롬프트 생성용 

    for data in label_data:
        if data["picture"] == THEMA:
            label_keyword = set(data["keywords"]) # 새, 꽃, 강, 나무, 산, 구름, 길
            label_prompt = data["prompt"] # 새: english, 꽃: english, 강: english
            break
    len_label_keyword = len(label_keyword)
    print("Base 키워드:", label_keyword)

    for user_keyword in results:
        print(user_keyword)
        is_trans_word = True
        
        # 멀티 스레드를 사용하여 모든 base_keyword에 대해 병렬로 유사성 검사
        with ThreadPoolExecutor() as executor:
            # 각 스레드가 요청하는 시간 사이에 0.5s의 간격을 준다.
            future_to_base_keyword = {executor.submit(check_similarity_multithreading, user_keyword, base_keyword, index * 0.2): 
                                        base_keyword for index, base_keyword in enumerate(label_keyword)}
            similarity_results = []
            
            for future in as_completed(future_to_base_keyword):
                th_result = future.result()
                if th_result[0]:
                    similarity_results.append(th_result[1:])
                    
        if len(similarity_results) != 0:
            max_score_keyword = max(similarity_results, key=lambda x: x[0])
            base_keyword = max_score_keyword[1]
            true_word.add(base_keyword) # true_word에 추가 (이때는 매칭되는 base 키워드가 들어감)
            label_keyword.remove(base_keyword) # 한 번 사용된 라벨은 label_keyword 자체에서 제거 (중복 채점 방지 및 연산 속도 증가)
            
            if base_keyword in label_prompt:
                whole_prompt_word.add(label_prompt[base_keyword]) # 생성용 단어에 주요 키워드 추가
                is_trans_word = False
                    
        if is_trans_word:
            translate_word.add(user_keyword) # 부가적인 정답 키워드 및 틀린 단어 번역할 준비
        
        print(true_word, translate_word)

        accuracy = len(true_word)/len_label_keyword

    return true_word, translate_word, accuracy, whole_prompt_word

if __name__ == "__main__":
    print(lex_rel_anal('예', '길_0101'))
    print()
    print(lex_rel_anal('예_0100', '길_0101'))