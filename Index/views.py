from django.shortcuts import render
from django.http import JsonResponse
import requests

# 웹 페이지를 여는 뷰
def index(request):
    return render(request, 'index.html')

# 오디오 파일을 네이버 STT로 전송하는 뷰
def send_audio_to_naver_stt(request):
    if request.method == 'POST' and request.FILES['audioFile']:
        audio_file = request.FILES['audioFile']
        client_id = ''  # 네이버 클라우드 플랫폼에서 발급받은 Client ID
        client_secret = ''  # 네이버 클라우드 플랫폼에서 발급받은 Client Secret
        url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor"

        headers = {
            "Content-Type": "application/octet-stream",
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
        }

        response = requests.post(url, data=audio_file, headers=headers)
        rescode = response.status_code
        if rescode == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({'error': 'Failed to process audio file'}, status=rescode)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
