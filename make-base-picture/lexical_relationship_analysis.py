import os
import urllib3
import json

# API 키 작성된 메모장 주소
keys_file_path = os.path.join('API', 'api_keys.txt')

# 파일에서 API 키를 로드하는 함수
with open(keys_file_path, 'r', encoding='utf-8') as file:
    keys = json.load(file)

# API 키 사용
AI_API_KEY = f"{keys['ai_api_keys']}"


def lex_rel_anal(firstWord, secondWord):
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseWWN/WordRel"
    accessKey = AI_API_KEY

    requestJson = {   
        "argument": {
            'first_word': firstWord,
            'second_word': secondWord,
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

    # 'Similarity' 키에 해당하는 값을 추출
    similarities = data['return_object']['WWN WordRelInfo']['WordRelInfo']['Similarity']

    average_score = 0
    # 각 알고리즘의 이름과 점수를 출력
    for sim in similarities:
        if sim['Algorithm'] not in ['Banerjee and Pedersen', 'Jiang and Conrath', 'Patwardhan', 'Leacock and Chodorow', 'Lin', 'Wu & Palmer']:
            average_score += sim['SimScore']
    average_score = average_score / 5
    return (True if average_score > 0.6 else False, average_score) 

if __name__ == "__main__":
    
    print(lex_rel_anal('입', '새'))
