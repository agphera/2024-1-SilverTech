import requests
import json
import io
import os
import base64
import urllib
from PIL import Image
import numpy as np


#%% API 키 불러오기
# API 키 작성된 메모장 주소
keys_file_path = os.path.join('API', 'api_keys.txt')

# 파일에서 API 키를 로드하는 함수
with open(keys_file_path, 'r', encoding='utf-8') as file:
    keys = json.load(file)

# API 키 사용
REST_API_KEY = f"{keys['rest_api_keys']}"

# 이미지 변환하기
def inpainting(image, mask, prompt):
    r = requests.post(
        'https://api.kakaobrain.com/v2/inference/karlo/inpainting',
        json = {
            'image': image,
            'mask': mask,
            'prompt': prompt
        },
        headers = {
            'Authorization': f'KakaoAK {REST_API_KEY}',
            'Content-Type': 'application/json'
        }
    )
    # 응답 JSON 형식으로 변환
    response = json.loads(r.content)
    return response

prompt = "the classroom chair, classroom desk, realistic"

# Base64 인코딩
def imageToString(img, mode='RGB'):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    my_encoded_img = base64.encodebytes(img_byte_arr.getvalue()).decode('ascii')
    return my_encoded_img

# Base64 문자열을 이미지로 변환
def stringToImage(base64_string, mode='RGB'):
    imgdata = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(imgdata))
    if mode == 'Grayscale':
        img = img.convert('L')  # Convert to Grayscale if mode is 'Grayscale'
    return img

# 이미지 파일 불러오기
img = Image.open('make-base-picture/template/classroom3.png')
mask = Image.open('make-base-picture/mask/mask1.png')

# 이미지를 Base64 인코딩하기
img_base64 = imageToString(img)


mask_base64 = imageToString(mask, mode='Grayscale')

# 이미지 변환하기 REST API 호출
response = inpainting(img_base64, mask_base64, prompt)
print(response)

# 응답의 첫 번째 이미지 생성 결과 출력하기
result = Image.open(urllib.request.urlopen(response.get("images")[0].get("image")))
result.show()