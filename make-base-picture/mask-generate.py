import json
import io
import os
import base64
import urllib
from PIL import Image
import numpy as np

# API 키 불러오기
keys_file_path = os.path.join('API', 'api_keys.txt')

# 파일에서 API 키를 로드하는 함수
with open(keys_file_path, 'r', encoding='utf-8') as file:
    keys = json.load(file)

# API 키 사용
REST_API_KEY = keys.get('rest_api_keys')

# Base64 인코딩
def imageToString(img, mode='RGB'):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    my_encoded_img = base64.encodebytes(img_byte_arr.getvalue()).decode('ascii')
    return my_encoded_img

# 마스크 생성
def generateMask(image_shape, black_regions):
    mask = np.ones(image_shape[:2], dtype=np.uint8) * 255  # 모두 흰색으로 채웁니다.

    # 마스크에 검은색 영역을 추가합니다.
    for region in black_regions:
        x, y, width, height = region
        mask[y:y+height, x:x+width] = 0

    mask = Image.fromarray(mask)
    mask.save('make-base-picture/mask/sky1_mask1.png')
    return mask

# 이미지 파일 불러오기
img = Image.open('make-base-picture/template/sky1.png')

# 마스크 생성
black_regions = [(200, 400, 300, 300), (700, 200, 200, 200)]  # 왼쪽 상단과 오른쪽 하단에 검은색 영역 추가
mask = generateMask(img.size, black_regions)

# 마스크를 이미지로 변환 후 Base64 인코딩
mask_base64 = imageToString(mask, mode='Grayscale')

print("마스크 생성이 완료되었습니다.")
