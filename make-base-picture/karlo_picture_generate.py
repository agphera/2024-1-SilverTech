# REST API 호출, 이미지 파일 처리에 필요한 라이브러리
import requests
import json
import urllib
import os
import json
from PIL import Image

NEGATIVE_PROMPT = 'out of frame, low resolution, blurry, worst quality, fuzzy, lowres, text, low quality, normal quality, signature, watermark, grainy, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, body out of frame, watermark, distorted face, bad anatomy, missing anatomy, missing body, missing face, missing legs, missing fingers, missing feet, missing toe, fewer digits, extra limbs, extra anatomy, extra face, extra arms, extra fingers, extra hands, extra legs, extra feet, extra toe, mutated hands, ugly, mutilated, disfigured, mutation, bad proportions, cropped head, cross-eye, mutilated, distorted eyes, strabismus, skin blemishes, Japan, China, Japanese, Chinese, Japanese language, Chinese language'

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
def t2i(prompt):
    negative_prompt = prompt[1]
    prompt = prompt[0]
    r = requests.post(
        'https://api.kakaobrain.com/v2/inference/karlo/t2i',
        json = {
            "version": "v2.1",
            "prompt": prompt,
            "negative_prompt": negative_prompt, 
            'seed': [777],
            'upscale': False,
            'prior_num_inference_steps': 20,
            'prior_guidance_scale': 10.0,
            'num_inference_steps': 70,
            'guidance_scale': 5.0,
            'face_refiner': {
                'bbox_size_threshold': 1.0,
                'bbox_filter_threshold': 1.0,
                'restoration_repeats': 3.0,
                'weight_sft': 0.5
            }
        },
        headers = {
            'Authorization': f'KakaoAK {REST_API_KEY}',
            'Content-Type': 'application/json'
        }
    )
    # 응답 JSON 형식으로 변환
    response = json.loads(r.content)
    return response

def make_prompt(subject):
    # 각 주제에 맞게 작성한 키워드를 불러와 템플릿에 맞춰 프롬프트 완성
    with open('make-base-picture/base-picture/keywords.json') as f:
        keyword_data = json.load(f)
        keywords = keyword_data[subject]

    # prompt_template = "clear style, appropriate distance between objects, purest form of minimalistic perfection, the {subject}-themed {word1} and {word2} and {word3}, high-end graphic illustration, high contrast, realistic colors."
    # prompt_template = "clear style, the {subject}-themed {word1} and {word2} and {word3} by Kim Hong-do, Korean traditional artist."
    # prompt_template = "The {subject}-themed {word1} and {word2} and {word3} by Kim Hong-do, Korean traditional artist."
    prompt_template = "In modern and contemporary history, Korea, and East Asia, The {subject}-themed {word1} and {word2} and {word3}, Simple, Clear style."
    
    prompt = prompt_template.format(subject=subject, word1=keywords[0], word2=keywords[1], word3=keywords[2])

    return (prompt, NEGATIVE_PROMPT)

if __name__ == "__main__":
    # 만들어낼 그림 주제
    """ 
    subject: classroom, park, mountain, beach, sky 
    + subject: stream
    """
    subject = "stream"
    version = '4'

    # 프롬프트에 사용할 제시어
    prompt = make_prompt(subject)
    print(prompt)

    # 이미지 생성하기 REST API 호출
    response = t2i(prompt)

    # 응답의 첫 번째 이미지 생성 결과 출력하기
    result = Image.open(urllib.request.urlopen(response.get("images")[0].get("image")))
    result.show()

    result.save(f'make-base-picture/base-picture/{subject+version}-base-picture.png','PNG') 