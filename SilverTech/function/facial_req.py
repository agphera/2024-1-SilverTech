#! /usr/bin/python

# 필요한 패키지를 임포트합니다
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2

# 'currentname'을 초기화하여 새로운 사람이 식별될 때만 트리거되도록 합니다.
currentname = "unknown"
# train_model.py에서 생성된 encodings.pickle 파일 모델로부터 얼굴을 식별합니다.
encodingsP = "SilverTech/static/encodings.pickle"

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

        print(data['names'])
        print(matches)        

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
                currentname = name
                
                print(currentname.replace('User_images_', '')) #이거 들고가면 됨!!! -> 숫자로 넘어가게하기 
                vs.stop() # 비디오 스트림을 종료합니다.
                fps.stop() # FPS 카운터를 종료합니다.
                cv2.destroyAllWindows() # 모든 OpenCV 창을 닫습니다.
                exit() # 프로그램을 종료합니다.

