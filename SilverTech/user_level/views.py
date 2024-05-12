import json
import random
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from .models import BasePictures, User, UserAccuracy, UserProceeding
from function.server_use import scoring_points

picture_number_by_level = [2, 5, 3, 5, 3] #[2,5,3]만 해두니 level 3과 4에서 list over되어 5, 3 추가함

# http://127.0.0.1:8000/picture-load/

# Create your views here.
def test_picture_load(request):
    return render(request, "test-image-load.html") # templates 폴더 안에 test-image-load.html가 존재함

#회원정보 확인
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
        return error_response  # 오류 응답 반환

    try:
        level = user_proceeding.level
        picture_level = level if level <= 2 else level - 2  # 레벨 조정 로직
        request.session['picture_level'] = picture_level

        # last_order에 해당하는 그림을 가져옴
        base_picture = BasePictures.objects.get(level=picture_level, order=user_proceeding.last_order)
        return render(request, 'level-image.html', {
            'level': level,
            'url': base_picture.url,
            'order': base_picture.order
        })
    except BasePictures.DoesNotExist:
        return JsonResponse({'error': 'Base picture not found'}, status=404)


# 다음 order의 그림을 가져오는 함수
@csrf_exempt
def change_base_picture(request):
    data = json.loads(request.body.decode('utf-8'))
    is_order = data.get('is_order', False)

    try:
        user_id = request.session.get('user_id')
        level = request.session.get('level')
        picture_level = request.session.get('picture_level')
        user_proceeding = UserProceeding.objects.get(user_id=user_id)

        # 난이도 3, 4를 처리하되 picture_number_by_level 범위 확인
        if level >= len(picture_number_by_level):
            return JsonResponse({'error': 'Level out of range'}, status=400)
        
        # 원래는 조건을 user_proceeding.is_order로 해서 사용자에 따라 구분해야함.
        # 현재는 테스트를 위해 is_order 값 자체를 request로 받고 있음
        # 난이도 3, 4일때 역순으로 출력
        if level == 3 or level == 4:
            if is_order:
                # 1. last_order를 역순으로 업데이트
                user_proceeding.last_order = (user_proceeding.last_order - 1 + picture_number_by_level[level]) % picture_number_by_level[level]
                # 2. 역순 업데이트된 last_order에 맞는 그림을 불러옴
                base_picture = BasePictures.objects.get(level=picture_level, order=user_proceeding.last_order)
            else:
                # 1. 동일 레벨에서 무작위로 base_picture 선정 (직전에 본 그림은 제외)
                base_picture_list = BasePictures.objects.filter(level=picture_level).exclude(order=user_proceeding.last_order)
                base_picture = random.choice(base_picture_list)
                # 2. 뽑은 그림으로 last_order 업데이트
                user_proceeding.last_order = base_picture.order
        else:
            if is_order:
                # 1. last_order 업데이트
                user_proceeding.last_order = (user_proceeding.last_order + 1) % picture_number_by_level[level]
                # 2. last_order에 맞는 그림을 불러옴
                base_picture = BasePictures.objects.get(level=picture_level, order=user_proceeding.last_order)
            else:
                # 랜덤 동일
                base_picture_list = BasePictures.objects.filter(level=picture_level).exclude(order=user_proceeding.last_order)
                base_picture = random.choice(base_picture_list)
                user_proceeding.last_order = base_picture.order

        user_proceeding.save() # 변경된 last_order 값을 DB에 반영
        
        return JsonResponse({'url': base_picture.url, 'order': base_picture.order}, status=200)

    except UserProceeding.DoesNotExist:
        return JsonResponse({'error': 'User proceeding not found'}, status=404)
    except BasePictures.DoesNotExist:
        return JsonResponse({'error': 'Base picture not found'}, status=404)
    except IndexError:
        return JsonResponse({'error': 'Index out of range'}, status=400)


@require_http_methods(["GET"])
def get_picture(request):

    picture_id = request.GET.get('picture', None)
    
    if picture_id:
        try:
            picture_id = int(picture_id) - 1
            picture = BasePictures.objects.get(picture_id=picture_id)
            return JsonResponse({'url': picture.url})
        except BasePictures.DoesNotExist:
            return JsonResponse({'error': 'Button not found'}, status=404)
    else:
        return JsonResponse({'error': 'No button name provided'}, status=400)

# 사용자 난이도 조정
@require_http_methods(["POST"])
@csrf_exempt 
def adjust_level(request):
    user_id = request.session.get('user_id') # 세션에서 user_id를 가져오기

    # user_id가 없으면 인증되지 않은 사용자로 간주하고 오류 메시지를 반환
    if not user_id:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    # 요청에서 JSON 데이터를 파싱 후 'action'값 추출
    data = json.loads(request.body.decode('utf-8'))
    action = data.get('action')
    try:
        user_proceeding = UserProceeding.objects.get(user__user_id=user_id)
        if action == 1 and user_proceeding.level < 4: # action 값이 1이면 난이도를 증가
            user_proceeding.level += 1
        elif action == -1 and user_proceeding.level > 0: # action 값이 -1이면 난이도를 감소
            user_proceeding.level -= 1
        user_proceeding.save() # 변경된 난이도 정보를 데이터베이스에 저장

        # 난이도 정보 업데이트
        request.session['level'] = user_proceeding.level
        request.session['picture_level'] = user_proceeding.level if user_proceeding.level <= 2 else user_proceeding.level - 2

        return JsonResponse({'new_level': user_proceeding.level}, status=200)
    except UserProceeding.DoesNotExist:
        return JsonResponse({'error': 'User proceeding not found'}, status=404)
    
# 난이도 자동 조정 구현 테스트 필요    
@csrf_exempt
def adjust_level_with_accuracy(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    # JSON 데이터에서 accuracy 값을 추출
    data = json.loads(request.body)
    accuracy = data.get('accuracy', 0)  # 기본값 설정

    try:
        user_accuracy = UserAccuracy.objects.get(user_id=user_id)
        user_proceeding = UserProceeding.objects.get(user=user_id)

        if accuracy >= 0.6:
            user_accuracy.successive_correct += 1
            user_accuracy.successive_wrong = 0 #상 기록시 하 리셋
        elif accuracy < 0.2:
            user_accuracy.successive_wrong += 1
            user_accuracy.successive_correct = 0 #하 기록시 상 리셋
        else:
            user_accuracy.successive_correct = 0 #중 기록시 상,하 리셋
            user_accuracy.successive_wrong = 0

        # 연속 3회 '상'을 달성하거나, 연속 2회 '하'를 달성한 경우 레벨 조정
        if user_accuracy.successive_correct >= 3:
            if user_proceeding.level < 4:
                user_proceeding.level += 1
            user_accuracy.successive_correct = 0
        elif user_accuracy.successive_wrong >= 2:
            if user_proceeding.level > 0:
                user_proceeding.level -= 1
            user_accuracy.successive_wrong = 0

        user_proceeding.save()
        user_accuracy.save()

        return JsonResponse({
            'new_level': user_proceeding.level,
            'successive_correct': user_accuracy.successive_correct,
            'successive_wrong': user_accuracy.successive_wrong
        }, status=200)

    except UserAccuracy.DoesNotExist:
        return JsonResponse({'error': 'User accuracy record not found'}, status=404)
    except UserProceeding.DoesNotExist:
        return JsonResponse({'error': 'User proceeding not found'}, status=404)