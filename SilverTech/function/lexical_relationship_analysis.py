import os
import urllib3
import json
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


    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8", "Authorization": accessKey},
        body=json.dumps(requestJson)
    )

    # JSON 데이터를 파이썬 딕셔너리로 변환
    data = json.loads(response.data)

    print(data)

    # 'Similarity' 키에 해당하는 값을 추출
    similarities = data['return_object']['WWN WordRelInfo']['WordRelInfo']['Similarity']

    average_score = 0
    # 각 알고리즘의 이름과 점수를 출력
    for sim in similarities:
        if sim['Algorithm'] not in ['Banerjee and Pedersen', 'Jiang and Conrath', 'Patwardhan', 'Leacock and Chodorow', 'Lin', 'Wu & Palmer']:
            average_score += sim['SimScore']
    average_score = average_score / 5
    return (True if average_score > 0.6 else False, average_score) 

def check_similarity_multithreading(user_keyword, base_keyword):
    """
    lex_rel_anal 함수를 호출하고 결과를 반환하는 래퍼 함수.
    """
    similarity_result, average_score = lex_rel_anal(user_keyword, base_keyword)
    return similarity_result, average_score, base_keyword

def user_base_similarity(THEMA, results):
    with open('../make-base-picture/base-picture/base-picture-labeling.json', 'r', encoding='utf-8') as f:
        label_data = json.load(f)

    true_word = set() # 정답률 체크
    false_word = set() # 오답단어 번역용
    whole_prompt = set() # 프롬프트 생성용 

    for data in label_data:
        if data["picture"] == THEMA:
            label_keyword = set(data["keywords"]) # 새, 꽃, 강, 나무, 산, 구름, 길
            label_prompt = data["prompt"] # 새: english, 꽃: english, 강: english
            break
    len_label_keyword = len(label_keyword)
    print("Base 키워드:", label_keyword)

    for user_keyword in results:
        print(user_keyword)
        found_word = False
        
        # 멀티 스레드를 사용하여 모든 base_keyword에 대해 병렬로 유사성 검사
        with ThreadPoolExecutor() as executor:
            future_to_base_keyword = {executor.submit(check_similarity_multithreading, user_keyword, base_keyword): base_keyword for base_keyword in label_keyword}
            
            similarity_results = []

            for future in as_completed(future_to_base_keyword):
                th_result = future.result()
                if th_result[0]:
                    similarity_results.append(th_result[1:])
                    
            if len(similarity_results) != 0:
                found_word = True
                max_score_keyword = max(similarity_results, key=lambda x: x[0])
                base_keyword = max_score_keyword[1]
                true_word.add(base_keyword) # true_word에 추가 (이때는 매칭되는 base 키워드가 들어감)
                label_keyword.remove(base_keyword) # 한 번 사용된 라벨은 label_keyword 자체에서 제거 (중복 채점 방지 및 연산 속도 증가)
                
                if base_keyword in label_prompt:
                    whole_prompt.add(label_prompt[base_keyword])
                    
        if not found_word:
            false_word.add(user_keyword)
        print(true_word, false_word)
    return true_word, false_word, len(true_word)/len_label_keyword, whole_prompt

    # for user_keyword in results:
    #     print(user_keyword)
    #     found_word = False
    #     for base_keyword in label_keyword:
    #         #print(user_keyword,"와 ",base_keyword,"를 비교하겠습니다.") #비교 확인용 코드
    #         similarity_result, _ = lex_rel_anal(user_keyword, base_keyword)

    #         if similarity_result:
    #             found_word = True
    #             true_word.add(base_keyword) # true_word에 추가 (이때는 매칭되는 base 키워드가 들어감)
    #             label_keyword.remove(base_keyword) # 한 번 사용된 라벨은 label_keyword 자체에서 제거 (중복 채점 방지 및 연산 속도 증가)
                
    #             if base_keyword in label_prompt:
    #                 whole_prompt.add(label_prompt[base_keyword])
    #             break
    #     if not found_word:
    #         false_word.add(user_keyword)
    #     print(true_word, false_word)

if __name__ == "__main__":
    print(lex_rel_anal('예', '길_0101'))
    print()
    print(lex_rel_anal('예_0100', '길_0101'))