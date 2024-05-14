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
            # DB에서 해당 사용자의 난이도 정보를 가져옴
            user = User.objects.get(name=user_name)
        except User.DoesNotExist:
            # 사용자가 존재하지 않는 경우 새로운 사용자를 생성하고 저장
            user = User(name=user_name)
            user.save()
            # 새로운 사용자에 대해 UserProceeding을 초기화
            user_proceeding = UserProceeding(user=user, level=1, last_order=0, is_order=0)
            user_proceeding.save()
        else:
            # 사용자가 존재하는 경우 UserProceeding 가져오기
            try:
                user_proceeding = UserProceeding.objects.get(user=user)
            except UserProceeding.DoesNotExist:
                # UserProceeding이 존재하지 않을 경우 error
                return None, JsonResponse({'error': 'User proceeding not found'}, status=404)
        
        # 세션에 사용자 정보 저장
        request.session['user_name'] = user_name
        request.session['user_id'] = user.user_id
        request.session['level'] = user_proceeding.level

        return user_proceeding, None  # UserProceeding 객체와 None 반환
    else:
        return None, JsonResponse({'error': 'No name provided'}, status=400)

#base그림 출력
def load_base_picture(request):
    user_proceeding, error_response = fetch_user_info(request)
    if error_response:
        return error_response  # 오류 응답 반환

    try:
        level = user_proceeding.level
        request.session['picture_level'] = level if level <= 2 else level - 2  # 레벨 조정 로직

        # last_order에 해당하는 그림을 가져옴
        base_picture = BasePictures.objects.get(level=level, order=user_proceeding.last_order)
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
        user_proceeding = UserProceeding.objects.get(user_id=user_id)

        if level >= len(picture_number_by_level):
            return JsonResponse({'error': 'Level out of range'}, status=400)

        if is_order:
            # is_order가 참일 때 역순 로직 적용 (레벨 3, 4에 대한 조건)
            if level == 3 or level == 4:
                # 역순으로 그림 업데이트
                new_order = (user_proceeding.last_order - 1 + picture_number_by_level[level]) % picture_number_by_level[level]
                user_proceeding.last_order = new_order
            else:
                # 기타 레벨에서는 정순 로직 적용
                new_order = (user_proceeding.last_order + 1) % picture_number_by_level[level]
                user_proceeding.last_order = new_order
        else:
            # is_order가 거짓일 때 랜덤 선택 로직 적용
            all_pictures = list(BasePictures.objects.filter(level=level).values_list('order', flat=True))
            seen_pictures = user_proceeding.seen_pictures or []
            available_pictures = [order for order in all_pictures if order not in seen_pictures]
            if not available_pictures:
                seen_pictures = []  # 이미 본 그림 목록 리셋
                available_pictures = all_pictures

            chosen_order = random.choice(available_pictures)
            user_proceeding.last_order = chosen_order
            seen_pictures.append(chosen_order)
            user_proceeding.seen_pictures = seen_pictures

        user_proceeding.save()

        base_picture = BasePictures.objects.get(level=level, order=user_proceeding.last_order)
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
    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    data = json.loads(request.body.decode('utf-8'))
    action = data.get('action')

    try:
        user_proceeding = UserProceeding.objects.get(user__user_id=user_id)
        old_level = user_proceeding.level
        if action == 1 and user_proceeding.level < 4:
            user_proceeding.level += 1
        elif action == -1 and user_proceeding.level > 0:
            user_proceeding.level -= 1

        # 레벨 변경이 있을 경우 last_order를 0으로 설정하고 seen_pictures 초기화
        if old_level != user_proceeding.level:
            user_proceeding.last_order = 0  # 항상 레벨 변경 시 0번 그림부터 시작
            user_proceeding.seen_pictures = [0]  # seen_pictures 초기화 및 첫 번째 그림 번호 추가
            user_proceeding.save()  # 변경 사항을 데이터베이스에 저장

            # 새 레벨과 last_order에 기반하여 이미지 URL 가져오기
            picture = BasePictures.objects.filter(level=user_proceeding.level, order=user_proceeding.last_order).first()
            if picture:
                image_url = picture.url
            else:
                image_url = None  # 해당 레벨과 순서에 맞는 그림이 없는 경우

            request.session['level'] = user_proceeding.level

            return JsonResponse({
                'new_level': user_proceeding.level,
                'first_picture_order': user_proceeding.last_order,
                'url': image_url
            }, status=200)
        
    except UserProceeding.DoesNotExist:
        return JsonResponse({'error': 'User proceeding not found'}, status=404)
    except BasePictures.DoesNotExist:
        return JsonResponse({'error': 'No base picture found for this level and order'}, status=404)
    
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