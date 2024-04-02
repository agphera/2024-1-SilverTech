# REST API 호출, 이미지 파일 처리에 필요한 라이브러리
import requests
import json
import urllib
import os
from PIL import Image

#%% API 키 불러오기
# API 키 작성된 메모장 주소
keys_file_path = os.path.join('API', 'api_keys.txt')

# 파일에서 API 키를 로드하는 함수
with open(keys_file_path, 'r', encoding='utf-8') as file:
    keys = json.load(file)

# API 키 사용
REST_API_KEY = f"{keys['rest_api_keys']}"

#%% Karlo 코드 실행
# 이미지 생성하기 요청
def t2i(prompt, negative_prompt):
    r = requests.post(
        'https://api.kakaobrain.com/v2/inference/karlo/t2i',
        json = {
            "version": "v2.1",
            "prompt": prompt,
            "negative_prompt": negative_prompt, 
            'seed': [660],
            'upscale': False,
            'prior_num_inference_steps': 20,
            'prior_guidance_scale': 10.0,
            'num_inference_steps': 70,
            'guidance_scale': 5.0,
        },
        headers = {
            'Authorization': f'KakaoAK {REST_API_KEY}',
            'Content-Type': 'application/json'
        }
    )
    # 응답 JSON 형식으로 변환
    response = json.loads(r.content)
    return response


# 프롬프트에 사용할 제시어
prompt = "There is a bright parasol on the beach and a beach view of colorful fish swimming near the coast by realitic."
negative_prompt = "scary, darkness, person, human-like"

# 이미지 생성하기 REST API 호출
response = t2i(prompt, negative_prompt)

# 응답의 첫 번째 이미지 생성 결과 출력하기
result = Image.open(urllib.request.urlopen(response.get("images")[0].get("image")))
result.show()

result.save('make-base-picture/base-picture/beach2-base-picture.png','PNG')