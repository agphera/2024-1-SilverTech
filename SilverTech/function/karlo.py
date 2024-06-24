# REST API 호출, 이미지 파일 처리에 필요한 라이브러리
import requests
import json
import urllib
import os
import threading
from tqdm import tqdm
from PIL import Image


#%% API 키 불러오기
# API 키 작성된 메모장 주소
keys_file_path = os.path.join('../API', 'api_keys.txt')

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
            'prior_num_inference_steps': 15,
            'prior_guidance_scale': 10.0,
            'num_inference_steps': 70,
            'guidance_scale': 10.0,
            'face_refiner': { # 얼굴 보정
                'bbox_size_threshold': 1.0,
                'bbox_filter_threshold': 0.2,
                'restoration_repeats': 5.0,
                'weight_sft': 0.25
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

classic_template_subjects = ["mountain", "park", "sky"] # 해당 subject(THEMA)는 classic 프롬프트 사용
CLASSIC_NEGATIVE_PROMPT = 'scary, a dividing line, darkness, person, human-like, complicated, stack, small creature, an alcoholic beverage, a moon, dirty, crowded, faint, ambiguous, box'

memory_template_subjects = ["stream", "farming"] # 해당 subject(THEMA)는 memory 프롬프트 사용
MEMORY_NEGATIVE_PROMPT = 'out of frame, low resolution, blurry, worst quality, fuzzy, lowres, text, low quality, signature, grainy, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, body out of frame, watermark, distorted face, bad anatomy, missing anatomy, missing body, missing face, missing legs, missing fingers, missing feet, missing toe, fewer digits, extra limbs, extra anatomy, extra face, extra arms, extra fingers, extra hands, extra legs, extra feet, extra toe, mutated hands, ugly, mutilated, disfigured, mutation, bad proportions, cropped head, cross-eye, mutilated, distorted eyes, strabismus, skin blemishes, Japan, China, Japanese, Chinese, Japanese language, Chinese language, Southeast Asia'

def make_prompt(subject, words = None):
# 각 주제에 맞게 작성한 키워드를 불러와 템플릿에 맞춰 프롬프트 완성
    print('수정된 버전')
    #1 base 그림을 라벨링한 데이터 로드
    with open('../make-base-picture/base-picture/keywords.json') as f:
        keyword_data = json.load(f)
        keywords = keyword_data[subject]
    
    if words != None: # 입력된 words가 없다면 기본 키워드를 사용해 프롬프트 생성 (base 그림 생성용)
        keywords = words

    #2 키워드 사이에 'and'를 넣어서 하나의 string으로 병합
    words_string = ' and '.join(keywords)

    #3 주제 뒤에 붙은 버전을 전처리 한 뒤, 주제에 맞게 사용할 프롬프트와 네거티브 프롬프트를 설정함
    subject = subject[:-1]
    if subject in classic_template_subjects:
        prompt = f"clear style, appropriate distance between objects, purest form of minimalistic perfection, the {subject}-themed {words_string}, high-end graphic illustration, high contrast, realistic colors."
        negative_prompt = CLASSIC_NEGATIVE_PROMPT
    elif subject in memory_template_subjects:
        prompt = f"The {subject}-themed {words_string}, Korea, East Asia, Korea, clear style, In modern and contemporary history, pastel colors, Korea."
        negative_prompt = MEMORY_NEGATIVE_PROMPT

    return (prompt, negative_prompt)


def show_pic(response):
    result = Image.open(urllib.request.urlopen(response.get("images")[0].get("image")))
    result.show()

def process_subject(subject, progress):   
    # 프롬프트에 사용할 제시어
    prompt = make_prompt(subject)

    # 이미지 생성하기 REST API 호출
    response = t2i(prompt)

    # 응답의 첫 번째 이미지 생성 결과 추출
    result = Image.open(urllib.request.urlopen(response.get("images")[0].get("image")))

    # 결과 이미지 저장
    result.save(f'make-base-picture/base-picture/{subject}-base-picture.png', 'PNG')
    progress.update(1)

def make_all_base_picture():
    subject_list = ['mountain1', 'mountain2', 'park1', 'park2', 'sky1', 'sky2', 'stream1', 'stream2', 'farming1', 'farming2']
    
    # 진행 상태를 업데이트하기 위한 tqdm 객체 생성
    progress = tqdm(total=len(subject_list))

    # 각 주제에 대해 별도의 스레드 생성 및 시작
    threads = []
    for subject in subject_list:
        thread = threading.Thread(target=process_subject, args=(subject, progress))
        threads.append(thread)
        thread.start()

    # 모든 스레드가 완료될 때까지 대기
    for thread in threads:
        thread.join()
