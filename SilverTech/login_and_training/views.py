
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import os
import json
import heapq
from function.server_use import scoring_points, make_picture
from django.urls import reverse  # reverse 함수를 사용합니다.

#모델 추가 학습
from imutils import paths
import shutil  # 폴더 삭제에 사용됩니다.
import face_recognition
import pickle
import cv2

#웹 캠 이용해서 사진 저장 
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import numpy as np

# API 키 작성된 메모장 주소
keys_file_path = os.path.join('../API', 'api_keys.txt')

# 파일에서 API 키를 로드하는 함수
with open(keys_file_path, 'r', encoding='utf-8') as file:
    keys = json.load(file)

# API 키 사용
NAVER_API_KEY_ID = f"{keys['naver_api_keys_id']}"
NAVER_API_KEY = f"{keys['naver_api_keys']}"

folder_counter = 0

# 웹에서 받아온 이미지 저장
# 입력: 이미지 데이터
# 반환: 없음
# 출력물: 새로운 회원의 숫자 정보
@csrf_exempt
def upload_image(request):
    global folder_counter
    path = None
    full_path = None

    if request.method == 'POST':
        try:
            images = request.FILES.getlist('photo')

            base_folder_name = 'User_images'
            folder_name = f"{base_folder_name}_{folder_counter}"
            directory_path = os.path.join(settings.MEDIA_ROOT, folder_name)
        
            
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            
            image_counter = 0
            full_paths = []
            for image in images:
                image_counter += 1

                file_name = os.path.join(folder_name, f"image_{image_counter}.jpg")

                path = default_storage.save(file_name, ContentFile(image.read()))
                full_path = os.path.join(settings.MEDIA_ROOT, path)
                print(f"Image {image_counter} uploaded successfully to {full_path}")
                full_paths.append(full_path)
            
            request.session['user_name'] = str(folder_counter)
            folder_counter = folder_counter + 1
            #del request.session['folder_counter']
            return train_model_again(request, directory_path)

        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



# 얼굴 인식 인공지능 모델 학습 및 입력으로 받아온 이미지 폴더 경로에 해당하는 폴더 삭제
# 입력: 이미지 데이터 불러올 주소
# 반환: 없음
# 출력물: 새롭게 학습된 모델 파일(./static/encodings.pickle)
def train_model_again(request, directory_path):
    encoding_file = "./static/encodings.pickle"
    
    # 인코딩 파일 존재 여부 확인 및 초기화
    if os.path.exists(encoding_file):
        # 기존에 저장된 얼굴 인코딩과 이름을 불러옵니다.
        with open(encoding_file, "rb") as f: 
            data = pickle.load(f)
        knownEncodings = data["encodings"]
        knownNames = data["names"]
    else:
        # 파일이 없으면 초기화
        print("[INFO] 인코딩 파일이 없으므로 새로 생성합니다.")
        knownEncodings = []
        knownNames = []

    # 새로운 이미지 경로 설정 (새로운 학습 데이터 경로)
    newImagePaths = list(paths.list_images(directory_path))

    # 새로운 이미지 데이터에 대해 루프를 돌면서 처리
    for i, imagePath in enumerate(newImagePaths):
        print("[INFO] processing image {}/{}".format(i + 1, len(newImagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        if not os.path.exists(imagePath):
            print("이미지 파일이 존재하지 않습니다:", imagePath)
        if not os.access(imagePath, os.R_OK):
            print("파일에 읽기 권한이 없습니다:", imagePath)

        print('imagePath:', imagePath)
        # image = cv2.imread(imagePath)
        img_array = np.fromfile(imagePath, np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model="cnn")
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

    # 수정된 인코딩과 이름 데이터를 다시 pickle 파일로 저장합니다.
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    with open(encoding_file, "wb") as f: 
        f.write(pickle.dumps(data))
    
    # 폴더가 존재하는지 확인
    if os.path.exists(directory_path):
        # 폴더 삭제
        shutil.rmtree(directory_path)
        print(f"{directory_path} 폴더가 성공적으로 삭제되었습니다.")
    else:
        print(f"{directory_path} 폴더를 찾을 수 없습니다.")

    return JsonResponse({'status': '^*^', 'message': 'Good~'}, status=200)


# 얼굴 인식 인공지능을 이용한 사람 구분 시스템
# 입력: 없음
# 반환: 없음
# 출력: 회원의 숫자 데이터
@csrf_exempt
def login_order(request):
    try:
        if request.method == 'POST':
            folder_name = "login"
            directory_path = os.path.join(settings.MEDIA_ROOT, folder_name)

            image = request.FILES.getlist('photo')[0]            
            # 경로 생성해서 이미지 저장
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            
            file_name = os.path.join(folder_name, "login_image.jpg")
            path = default_storage.save(file_name, ContentFile(image.read()))
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            print(f"Image uploaded successfully to {full_path}")

            # 인코딩된 회원 데이터 불러오기
            with open("./static/encodings.pickle", "rb") as f: 
                data = pickle.load(f)
            
            # 저장된 이미지를 형식에 맞게 불러옴 
            img_array = np.fromfile(full_path, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # cnn 모델을 사용해 얼굴 비교
            boxes = face_recognition.face_locations(rgb, model="cnn")
            encodings = face_recognition.face_encodings(rgb, boxes)
            
            for encoding in encodings:
                # 입력 이미지의 각 얼굴을 알려진 인코딩과 비교하여 일치하는지 시도합니다.
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Guest"
                # 일치하는 경우가 있는지 확인합니다.
                if True in matches:
                    print('일치하는 경우 있음')
                    # 모든 일치하는 얼굴의 인덱스를 찾은 다음 각 인식된 얼굴에 대한 투표 횟수를 계산하기 위한 사전을 초기화합니다.
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # 일치하는 인덱스를 반복하고 각 인식된 얼굴에 대한 카운트를 유지합니다.
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    
                    # 가장 많은 표를 받은 얼굴을 결정합니다(동점인 경우 Python은 사전의 첫 번째 항목을 선택합니다).
                    name = max(counts, key=counts.get)

            # Guest 혹은 로그인된 정보를 session에 저장 
            request.session['user_name'] = name.replace('User_images_', '')

            # 폴더가 존재하는지 확인
            if os.path.exists(directory_path):
                # 폴더 삭제
                shutil.rmtree(directory_path)
                print(f"{directory_path} 폴더가 성공적으로 삭제되었습니다.")
            else:
                print(f"{directory_path} 폴더를 찾을 수 없습니다.")

            return JsonResponse({'status': '사람 구분 성공적', 'message': 'Good~'}, status=200)
    except Exception as e:
        print(f"An error occurred: {e}")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

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

        theme = request.session.get('theme')
        print('theme:',theme)
        
        if "text" in data:            
            accuracy, true_word, whole_prompt = scoring_points(data['text'], theme)
            request.session['accuracy'] = accuracy

            data['accuracy'] = accuracy
            data['len_true_word'] = len(true_word)
            data['p'] = list(whole_prompt)

        print(data)
        # accuracy가 일정 값 이상이면 정답 처리 -> 다음 그림을 보여줘야 하는데...

        response_to_client = JsonResponse(data, safe=False)
        response_to_client["Access-Control-Allow-Origin"] = "*"
        response_to_client["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response_to_client["Access-Control-Allow-Headers"] = "Content-Type"
        print('최종 반환:', response_to_client)
        return response_to_client
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    

# 전역 변수로 오류 횟수 카운팅
error_counter = {'count': 0}

@csrf_exempt
def proxy_to_naver_stt9(request):
    if request.method == 'POST' and request.FILES.get('audioFile'):
        naver_api_url = 'https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor'
        headers = {
            "Content-Type": "application/octet-stream",
            "X-NCP-APIGW-API-KEY-ID": NAVER_API_KEY_ID,
            "X-NCP-APIGW-API-KEY": NAVER_API_KEY,
        }

        audio_file = request.FILES['audioFile'].read()
        try_count = 0
        while try_count < 3:
            response = requests.post(naver_api_url, headers=headers, data=audio_file)
            data = response.json()

            if "text" in data:
                print('초기 데이터:',data)

                theme = request.session.get('theme')
                print('theme:',theme)

                accuracy, true_word, whole_prompt = scoring_points(data['text'], theme)
                request.session['accuracy'] = accuracy

                data['accuracy'] = accuracy
                data['len_true_word'] = len(true_word)
                data['p'] = list(whole_prompt)
                response_to_client = JsonResponse(data, safe=False)
                response_to_client["Access-Control-Allow-Origin"] = "*"
                response_to_client["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                response_to_client["Access-Control-Allow-Headers"] = "Content-Type"
                error_counter['count'] = 0  # 입력이 잘되거나 오류가 없을 시 카운트 초기화
                return response_to_client

            error_counter['count'] += 1
            if error_counter['count'] == 3:  # 오류가 3번 발생하면 종료
                return JsonResponse({'error': 'Error count exceeded. Please try again.'}, status=500)

            try_count += 1

        return JsonResponse({'error': 'Failed to convert audio to text after 3 attempts'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def make_pic_karlo(request):
    if request.method == 'POST':
        print('함수 호출 완료')
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        theme = request.session.get('theme')

        whole_prompt = body_data.get('text', '')
        image_response = make_picture(whole_prompt, theme)
        image_url = image_response['images'][0]['image']
        data = {'image_url': image_url}

        # 세션에서 'user_history'를 가져오고 없으면 빈 리스트로 초기화
        user_history = request.session.get('user_history', [])
        
        # max heap에 이미지 url 저장
        accuracy = request.session.get('accuracy')
        heapq.heappush(user_history, [-accuracy, image_url])
        
        print(user_history)
        
        # 세션에 업데이트된 리스트 저장
        request.session['user_history'] = user_history

        print(data)

        response_to_client = JsonResponse(data, safe=False)
        response_to_client["Access-Control-Allow-Origin"] = "*"
        response_to_client["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response_to_client["Access-Control-Allow-Headers"] = "Content-Type"

        return response_to_client

def fetch_user_history(request):
    # 세션에서 'user_history'를 가져오고 없으면 빈 리스트로 초기화
    user_history = request.session.get('user_history', [])
    
    # 상위 5개의 점수를 가져오기 위해 max heap에서 값을 꺼내기
    top_scores = heapq.nsmallest(5, user_history)
    
    # url 리스트만 반환
    top_scores_url = [item[1] for item in top_scores]
    
    # JSON 형식으로 반환
    return JsonResponse({'urls': top_scores_url})


# urls.py
from django.urls import path
from .views import proxy_to_naver_stt

urlpatterns = [
    path('api/naver-stt/', proxy_to_naver_stt, name='naver_stt_proxy'),
]

@csrf_exempt 
def StartingPage(request): #
    if 'user_name' in request.session:
        return redirect('picture-load/picture-training')
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

@csrf_exempt
def logout_view(request):
    try:
        del request.session['user_name']
    except KeyError:
        pass
    return redirect(reverse('StartingPage'))
