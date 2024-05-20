#! /usr/bin/python

# import the necessary packages
from imutils import paths
import face_recognition
#import argparse
import pickle
import cv2
import os

# 기존에 저장된 얼굴 인코딩과 이름을 불러옵니다.
with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)
knownEncodings = data["encodings"]
knownNames = data["names"]

# 새로운 이미지 경로 설정 (새로운 학습 데이터 경로)
newImagePaths = list(paths.list_images("../Media/User_images_2"))

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
with open("encodings.pickle", "wb") as f:
    f.write(pickle.dumps(data))
f.close()
