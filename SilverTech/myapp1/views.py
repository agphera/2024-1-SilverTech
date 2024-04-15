
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import os
import json

# API 키 작성된 메모장 주소
keys_file_path = os.path.join('../API', 'api_keys.txt')

# 파일에서 API 키를 로드하는 함수
with open(keys_file_path, 'r', encoding='utf-8') as file:
    keys = json.load(file)

# API 키 사용
NAVER_API_KEY_ID = f"{keys['naver_api_keys_id']}"
NAVER_API_KEY = f"{keys['naver_api_keys']}"

@csrf_exempt
def proxy_to_naver_stt(request):
    if request.method == 'POST' and request.FILES.get('audioFile'):

        naver_api_url = 'https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor'
        headers = {
            "Content-Type": "application/octet-stream",  # 오디오 파일의 유형에 따라 수정할 수 있습니다.
            "X-NCP-APIGW-API-KEY-ID": NAVER_API_KEY_ID,
            "X-NCP-APIGW-API-KEY": NAVER_API_KEY,
        }
        
        audio_file = request.FILES['audioFile'].read()
        response = requests.post(naver_api_url, headers=headers, data=audio_file)
        data = response.json()
        
        response_to_client = JsonResponse(data, safe=False)
        response_to_client["Access-Control-Allow-Origin"] = "*"
        response_to_client["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response_to_client["Access-Control-Allow-Headers"] = "Content-Type"
        return response_to_client
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

# urls.py
from django.urls import path
from .views import proxy_to_naver_stt
from function.server_use import scoring_points_create_picture

urlpatterns = [
    path('api/naver-stt/', proxy_to_naver_stt, name='naver_stt_proxy'),
]

@csrf_exempt
def index(request):
    return render(request, '../Frontend_UI/index.html')

def send_audio_to_naver_stt(request):
    if request.method == 'POST' and request.FILES.get('audioFile'):
        audio_file = request.FILES['audioFile'].read()  # 파일을 메모리에 로드합니다.
        url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor"

        headers = {
            "Content-Type": "application/octet-stream",  # 오디오 파일의 유형에 따라 수정할 수 있습니다.
            "X-NCP-APIGW-API-KEY-ID": NAVER_API_KEY_ID,
            "X-NCP-APIGW-API-KEY": NAVER_API_KEY,
        }

        response = requests.post(url, data=audio_file, headers=headers)
        rescode = response.status_code
        if rescode == 200:
            response_data = response.json()
            # 응답 본문 내용을 콘솔에 출력합니다.
            print("네이버 음성 인식 API 응답:")
            print(response_data)
            accuracy = scoring_points_create_picture(response_data.json()['text'])
            print("정답률:", accuracy)
            return JsonResponse(response.json(), safe=False)
        else:
            # 네이버 API 응답 본문을 포함하여 오류 메시지를 개선합니다.
            return JsonResponse({'error': 'Failed to process audio file', 'message': response.text}, status=rescode)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


