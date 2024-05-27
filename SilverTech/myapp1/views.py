
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import os
import json
from function.server_use import scoring_points, make_picture
from .models import User, UserProceeding, BasePictures, BasePictureThemes

# 필요한 패키지를 임포트합니다
from imutils.video import VideoStream
from imutils.video import FPS
import imutils
import time
from django.http import JsonResponse

#모델 추가 학습
from imutils import paths
import shutil  # 폴더 삭제에 사용됩니다.
import face_recognition
import pickle
import cv2
from user_level.views import login_to_training # app1의 함수를 가져옴

#웹 캠 이용해서 사진 저장 
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from PIL import Image
import numpy as np


# API 키 작성된 메모장 주소
keys_file_path = os.path.join('../API', 'api_keys.txt')

# 파일에서 API 키를 로드하는 함수
with open(keys_file_path, 'r', encoding='utf-8') as file:
    keys = json.load(file)

# API 키 사용
NAVER_API_KEY_ID = f"{keys['naver_api_keys_id']}"
NAVER_API_KEY = f"{keys['naver_api_keys']}"

@csrf_exempt
def proxy_to_naver_stt1(request):
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
    
from django.http import JsonResponse
from django.http import HttpResponseServerError
import requests

# 전역 변수로 오류 횟수 카운팅
error_counter = {'count': 0}

@csrf_exempt
def proxy_to_naver_stt(request):
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
                return HttpResponseServerError("Error count exceeded. Please try again.")

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
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)




# 얼굴 인식 인공지능 모델 학습 및 입력으로 받아온 이미지 폴더 경로에 해당하는 폴더 삭제
# 입력: 이미지 데이터 불러올 주소
# 반환: 없음
# 출력물: 새롭게 학습된 모델 파일(./static/encodings.pickle)
def train_model_again(request, directory_path):
    # 기존에 저장된 얼굴 인코딩과 이름을 불러옵니다.
    with open("./static/encodings.pickle", "rb") as f: 
        data = pickle.load(f)
    knownEncodings = data["encodings"]
    knownNames = data["names"]

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

        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

    # 수정된 인코딩과 이름 데이터를 다시 pickle 파일로 저장합니다.
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    with open("./static/encodings.pickle", "wb") as f:  #myapp1 바깥 쪽에 생김. 이거 위치 나중에 잡아주겠습니다. 
        f.write(pickle.dumps(data))
    

    # 폴더가 존재하는지 확인
    if os.path.exists(directory_path):
        # 폴더 삭제
        shutil.rmtree(directory_path)
        print(f"{directory_path} 폴더가 성공적으로 삭제되었습니다.")
    else:
        print(f"{directory_path} 폴더를 찾을 수 없습니다.")

    return login_to_training(request)




# 얼굴 인식 인공지능을 이용한 사람 구분 시스템
# 입력: 없음
# 반환: 없음
# 출력: 회원의 숫자 데이터
@csrf_exempt
def login_capture(request):
    # 'currentname'을 초기화하여 새로운 사람이 식별될 때만 트리거되도록 합니다.
    currentname = "Unknown"
    # train_model.py에서 생성된 encodings.pickle 파일 모델로부터 얼굴을 식별합니다.
    encodingsP = "./static/encodings.pickle"

    # 인코딩과 얼굴 검출을 위한 OpenCV의 Haar cascade를 로드합니다.
    print("[INFO] loading encodings + face detector...")
    data = pickle.loads(open(encodingsP, "rb").read())

    # 비디오 스트림을 초기화하고 카메라 센서가 예열될 시간을 줍니다.
    # MAC의 내장 웹캠을 사용하기 위해 src=0으로 설정합니다.
    vs = VideoStream(src=0).start()
    time.sleep(1.0)

    # FPS 카운터를 시작합니다.
    fps = FPS().start()

    # 비디오 파일 스트림에서 프레임을 반복 처리합니다.
    while True:
        try:
            # 스레드된 비디오 스트림에서 프레임을 캡처하고 크기를 조정합니다(처리 속도 향상을 위해).
            frame = vs.read()
            frame = imutils.resize(frame, width=500)
            # 얼굴 상자를 감지합니다.
            boxes = face_recognition.face_locations(frame)
            # 각 얼굴 경계 상자에 대한 얼굴 임베딩을 계산합니다.
            encodings = face_recognition.face_encodings(frame, boxes)
            names = []

            # 얼굴 임베딩을 반복합니다.
            for encoding in encodings:
                # 입력 이미지의 각 얼굴을 알려진 인코딩과 비교하여 일치하는지 시도합니다.
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Unknown"

                # 일치하는 경우가 있는지 확인합니다.
                if True in matches:
                    # 모든 일치하는 얼굴의 인덱스를 찾은 다음 각 인식된 얼굴에 대한 투표 횟수를 계산하기 위한 사전을 초기화합니다.
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # 일치하는 인덱스를 반복하고 각 인식된 얼굴에 대한 카운트를 유지합니다.
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # 가장 많은 표를 받은 얼굴을 결정합니다(동점인 경우 Python은 사전의 첫 번째 항목을 선택합니다).
                    name = max(counts, key=counts.get)

                    # 데이터셋에 있는 누군가가 식별되면 화면에 그들의 이름을 출력합니다.
                    if currentname != name:
                        print(currentname.replace('User_images_', '')) #이거 들고가면 됨!!! -> 숫자로 넘어가게하기 
                        
                        request.session['user_name'] = currentname.replace('User_images_', '')
                        
                        vs.stop() # 비디오 스트림을 종료합니다.
                        fps.stop() # FPS 카운터를 종료합니다.
                        cv2.destroyAllWindows() # 모든 OpenCV 창을 닫습니다.
                        
                        return login_to_training(request)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    # 루프를 탈출한 경우, 혹은 함수가 정상 종료된 경우 비디오 스트림을 정리합니다.
    vs.stop()
    fps.stop()
    cv2.destroyAllWindows()
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def login_order(request):
    if request.method == 'POST':
        try:
            images = request.FILES.getlist('photo')

            
            folder_name = f"Login"
            directory_path = os.path.join(settings.MEDIA_ROOT, folder_name)
        
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
 
            for image in images:
                file_name = os.path.join(folder_name, f"image.jpg")

                path = default_storage.save(file_name, ContentFile(image.read()))
                full_path = os.path.join(settings.MEDIA_ROOT, path)
                print(f"Image uploaded successfully to {full_path}")
                
            return JsonResponse({'status': '^*^', 'message': 'Good~'}, status=200)
        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)




    if request.method == 'POST' and 'image' in request.FILES:
        image_file = request.FILES['image']
        image = Image.open(image_file)
        rgb = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

        # 기존에 저장된 얼굴 인코딩과 이름을 불러옵니다.
        with open("./static/encodings.pickle", "rb") as f: 
            data = pickle.load(f)
        knownEncodings = data["encodings"]
        knownNames = data["names"]

        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append("unknown")  # You may change this to the actual name

        # 수정된 인코딩과 이름 데이터를 다시 pickle 파일로 저장합니다.
        data = {"encodings": knownEncodings, "names": knownNames}
        with open("./static/encodings.pickle", "wb") as f:
            f.write(pickle.dumps(data))

        response_data = {'message': 'Model training successful.'}
        return JsonResponse(response_data)
    else:
        response_data = {'error': 'No image found in the request.'}
        return JsonResponse(response_data, status=400)