
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import os
import json
from function.server_use import scoring_points, make_picture
from .models import User, UserProceeding, BasePictures

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
        print('초기 데이터:',data)

        if "text" in data:            
            accuracy, true_word, whole_prompt = scoring_points(data['text']) 
            data['accuracy'] = accuracy
            data['len_true_word'] = len(true_word)
            data['p'] = list(whole_prompt)

        # accuracy가 일정 값 이상이면 정답 처리 -> 다음 그림을 보여줘야 하는데...

        response_to_client = JsonResponse(data, safe=False)
        response_to_client["Access-Control-Allow-Origin"] = "*"
        response_to_client["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response_to_client["Access-Control-Allow-Headers"] = "Content-Type"
        print('최종 반환:', response_to_client)
        return response_to_client
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def make_pic_karlo(request):
    if request.method == 'POST':
        print('함수 호출 완료')
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        whole_prompt = body_data.get('text', '')
        image_response = make_picture(whole_prompt)
        data = {'image_url': image_response['images'][0]['image']}
        
        print(data)

        response_to_client = JsonResponse(data, safe=False)
        response_to_client["Access-Control-Allow-Origin"] = "*"
        response_to_client["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response_to_client["Access-Control-Allow-Headers"] = "Content-Type"

        return response_to_client

def fetch_user_info(request):
    #request에서 로그인 정보를 추출하는 코드 추후 추가
    #사용자 정보 임의 설정
    user_name = 'suchae'
    if user_name:
        try:
            # DB 접근해서 해당 사용자 난이도 정보를 가져옴
            user = User.objects.get(name=user_name)
            user_proceeding = UserProceeding.objects.get(user_id=user.user_id)

            # 세션에 사용자 정보 저장
            request.session['user_name'] = user_name
            request.session['user_id'] = user.user_id
            request.session['level'] = user_proceeding.level

            return user_proceeding, None  # 사용자 진행 객체와 None을 반환
        except User.DoesNotExist:
            return None, JsonResponse({'error': 'User not found'}, status=404)
        except UserProceeding.DoesNotExist:
            return None, JsonResponse({'error': 'User proceeding not found'}, status=404)
    else:
        return None, JsonResponse({'error': 'No name provided'}, status=400)

def load_base_picture(request):
    user_proceeding, error_response = fetch_user_info(request)
    if error_response:
        return error_response  # If error, return early

    try:
        # 사용자의 현재 레벨을 바탕으로 picture_level 계산
        current_level = user_proceeding.level
        # 예를 들어, picture_level은 현재 레벨보다 2 레벨 낮게 설정하되 최소 레벨은 1로 설정
        picture_level = max(1, current_level - 2)

        # DB에서 해당 레벨과 순서에 맞는 그림 정보를 가져옴
        base_picture = BasePictures.objects.get(level=picture_level, order=user_proceeding.last_order)
        return JsonResponse({'url': base_picture.url})  # 이미지 URL을 JSON 형식으로 전송
    except BasePictures.DoesNotExist:
        return JsonResponse({'error': 'Base picture not found'}, status=404)


# urls.py
from django.urls import path
from .views import proxy_to_naver_stt

urlpatterns = [
    path('api/naver-stt/', proxy_to_naver_stt, name='naver_stt_proxy'),
]

@csrf_exempt 
def StartingPage(request): #
    return render(request,'StartingPage.html')

@csrf_exempt
def Camera(request): #
    return render(request,'Camera.html')

@csrf_exempt
def index(request): #
    return render(request, 'index.html')

@csrf_exempt
def second_page(request):
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
            accuracy = (response_data.json()['text']) #주석
            print("정답률:", accuracy) #주석
            
            
            
            return JsonResponse({'text': response_data['text'], 'accuracy': accuracy})
            
            
            
            #return JsonResponse(response.json(), safe=False)
        
        else:
            # 네이버 API 응답 본문을 포함하여 오류 메시지를 개선합니다.
            return JsonResponse({'error': 'Failed to process audio file', 'message': response.text}, status=rescode)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


#웹 캠 이용해서 사진 저장 
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
@csrf_exempt
def upload_image(request):
    path = None
    full_path = None

    if request.method == 'POST':
        image = request.FILES.get('photo')
        if image:
            # 세션에서 이미지 카운터를 가져옵니다.
            image_counter = request.session.get('image_counter', 0)
            folder_counter = request.session.get('folder_counter', 1)
            image_counter += 1
            
            # 기본 폴더 이름 설정
            base_folder_name = 'User_images'
            
            # 실제 저장될 폴더 이름 설정
            folder_name = f"{base_folder_name}_{folder_counter}"
            
            # 파일 이름 설정
            file_name = os.path.join(folder_name, f"image_{image_counter}.jpg")
            
            # 이미지 저장
            path = default_storage.save(file_name, ContentFile(image.read()))
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            
            # 세션에 이미지 카운터와 폴더 카운터 업데이트
            request.session['image_counter'] = image_counter
            request.session['folder_counter'] = folder_counter
            
            print(f"Image {image_counter} uploaded successfully to {full_path}")
            
            # 10번째 이미지 후 세션 리셋 및 폴더 카운터 증가
            if image_counter >= 10:
                request.session['image_counter'] = 0  # 이미지 카운터 리셋
                print(folder_counter) #이거 들고가면 됨!!! 
                request.session['folder_counter'] = folder_counter + 1  # 폴더 카운터 증가
                
                
                train_model_again(os.path.join(settings.MEDIA_ROOT, folder_name))

            return JsonResponse({'message': 'Image uploaded successfully!', 'path': full_path})
        else:
            print("No image provided")
            return JsonResponse({'error': 'No image provided'}, status=400)
    else:
        print("Invalid request")
        return JsonResponse({'error': 'Invalid request'}, status=400)

#모델 추가 학습
from imutils import paths
import shutil  # 폴더 삭제에 사용됩니다.
import face_recognition
#import argparse
import pickle
import cv2
import os

def train_model_again(request):
    # 기존에 저장된 얼굴 인코딩과 이름을 불러옵니다.
    with open("../SilverTech/function/encodings.pickle", "rb") as f: 
        data = pickle.load(f)
    knownEncodings = data["encodings"]
    knownNames = data["names"]

    # 새로운 이미지 경로 설정 (새로운 학습 데이터 경로)
    newImagePaths = list(paths.list_images(request))

    # 새로운 이미지 데이터에 대해 루프를 돌면서 처리
    for (i, imagePath) in enumerate(newImagePaths):
        print("[INFO] processing image {}/{}".format(i + 1, len(newImagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

    # 수정된 인코딩과 이름 데이터를 다시 pickle 파일로 저장합니다.
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    with open("encodings.pickle", "wb") as f:  #myapp1 바깥 쪽에 생김. 이거 위치 나중에 잡아주겠습니다. 
        f.write(pickle.dumps(data))
    f.close()
    

    # 폴더가 존재하는지 확인
    if os.path.exists(request):
        # 폴더 삭제
        shutil.rmtree(request)
        print(f"{request} 폴더가 성공적으로 삭제되었습니다.")
    else:
        print(f"{request} 폴더를 찾을 수 없습니다.")





