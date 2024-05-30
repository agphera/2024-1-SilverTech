import json
import random
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import BasePictures, User, UserAccuracy, UserProceeding
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpRequest, HttpResponse


picture_number_by_level = [2, 5, 3, 5, 3] #[2,5,3]만 해두니 level 3과 4에서 list over되어 5, 3 추가함

# http://127.0.0.1:8000/picture-load/

# Create your views here.
def login_picture_load(request):
    return render(request, "test-login.html") # templates 폴더 안에 test-image-load.html가 존재함

# 회원정보 확인해서 로그인하거나 및 회원가입하는 함수
def fetch_user_info(request, user_name):
    if not user_name:
        return None, JsonResponse({'error': 'No name provided'}, status=400)
    
    user, created = User.objects.get_or_create(name=user_name)
    if created:
        UserProceeding.objects.create(user=user, level=1, last_order=0, is_order=1, seen_pictures=[], clear_level=[])
        UserAccuracy.objects.create(user=user, successive_correct=0, successive_wrong=0)
    
    user_proceeding = UserProceeding.objects.filter(user=user).first()
    if not user_proceeding:
        return None, JsonResponse({'error': 'User proceeding not found'}, status=404)

    request.session['user_name'] = user_name
    request.session['user_id'] = user.user_id
    print('fetch_user_info:', user_name)
    return user_proceeding, None

# 초기 동작 함수
@swagger_auto_schema(
    method='post',
    operation_id='move_to_training_site',
    operation_description='이 함수는 로그인/회원가입 정보를 받아 사용자를 훈련 사이트로 이동시킵니다.',
    tags=['Login'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='사용자 이름'),
        },
        required=['name'],
    ),
    responses={
        200: openapi.Response(description='성공적으로 훈련 사이트로 이동'),
        400: openapi.Response(description='잘못된 요청. 요청의 형식이 잘못되거나 필요한 정보가 누락되었습니다.'),
        404: openapi.Response(description='요청한 리소스를 찾을 수 없습니다.'),
    },
)
@swagger_auto_schema(  
    method='get',
    operation_id='fetch_training_site',
    operation_description='이 함수는 내부적으로 사용됩니다.',
    tags=['Login'],
    responses={
        200: openapi.Response(description='성공적으로 훈련 사이트를 가져옴'),
        400: openapi.Response(description='잘못된 요청. 요청의 형식이 잘못되었습니다.'),
        404: openapi.Response(description='요청한 훈련 사이트를 찾을 수 없습니다.'),
    },
)
@api_view(["GET", "POST"]) 
def login_to_training(request: HttpRequest):
    if request.method == "POST":
        name = request.session.get('user_name')
        print('login_to_training name:',name)
        
        user_proceeding, error_response = fetch_user_info(request, name)
        if error_response:
            return error_response  # 오류 응답 반환
        
        try:
            level = user_proceeding.level
            picture_level = level if level <= 2 else level - 2
            
            base_picture = BasePictures.objects.get(level=picture_level, order=user_proceeding.last_order)

            # 세션에 필요한 정보 저장
            request.session['level'] = level
            request.session['picture_url'] = base_picture.url
            request.session['picture_order'] = base_picture.order
            request.session['theme'] = base_picture.title

            print(request)
            # 같은 URL에서 GET 요청을 처리하도록 리다이렉트
            return redirect('../picture-training/')  
        except BasePictures.DoesNotExist:
            return JsonResponse({'error': 'Base picture not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        # GET 요청을 처리하고, 세션에서 정보를 가져와 템플릿을 렌더링
        context = {
            'name': request.session.get('user_name', 'Guest'),
            'level': request.session.get('level', 1),
            'url': request.session.get('picture_url', None),
            'order': request.session.get('picture_order', 0),
        }
        print(context)
        return render(request, 'index.html', context)

@swagger_auto_schema(
    method='post',  # 요청 메소드
    responses={  # 응답 형식
        200: openapi.Response(
            description="그림 URL과 순서 정보 반환",
            examples={
                "application/json": {
                    "url": "URL",
                    "order": 0,
                    "level": 1
                }
            }
        ),
        400: openapi.Response(description="잘못된 요청"),
        401: openapi.Response(description="인증 오류"),
        404: openapi.Response(description="정보를 찾을 수 없음",),
        500: openapi.Response(description="서버 내부 오류")
    },
    operation_description="사용자의 레벨과 진행 상태에 따라 적절한 그림을 반환하는 API",
    tags=['Base picture'], 
)
@api_view(["POST"])
def load_next_base_picture(request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        # 사용자 정확도와 진행 정보를 DB에서 가져옴
        user_accuracy = UserAccuracy.objects.get(user_id=user_id)
        user_proceeding = UserProceeding.objects.get(user__user_id=user_id)
        
        level_changed = check_change_level(request, user_accuracy, user_proceeding)
        
        if level_changed:
            base_picture = fetch_altered_level_base_picture(request, user_accuracy, user_proceeding)
        else:
            base_picture = fetch_same_level_base_picture(request, user_proceeding)
        
        request.session['level'] = user_proceeding.level
        request.session['picture_url'] = base_picture.url
        request.session['picture_order'] = base_picture.order
        request.session['theme'] = base_picture.title

        # 변경된 진행 정보와 정확도 정보 저장
        user_proceeding.save()
        user_accuracy.save()
        
        return JsonResponse({
            'level': user_proceeding.level,
            'order': user_proceeding.last_order,
            'url': base_picture.url
        }, status=200)

    except (UserAccuracy.DoesNotExist, UserProceeding.DoesNotExist, BasePictures.DoesNotExist) as e:
        return JsonResponse({'error': str(e)}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 다음 order의 그림을 가져오는 함수
def fetch_same_level_base_picture(request, user_proceeding):
    # 세션에서 레벨, 그림 레벨을 가져옴
    level = user_proceeding.level 
    picture_level = level if level <= 2 else level - 2  # 조정된 레벨 계산
    
    # 레벨이 설정된 범위를 벗어나면 오류 반환
    if level >= len(picture_number_by_level):
        return JsonResponse({'error': 'Level out of range'}, status=400)

    if user_proceeding.is_order:
        # is_order가 참일 때: 다음 순서의 그림을 역순으로 가져오는 로직
        if level == 3 or level == 4:
            # 레벨 3, 4일 때 역순으로 그림을 가져옴
            new_order = (user_proceeding.last_order - 1 + picture_number_by_level[level]) % picture_number_by_level[level]
            user_proceeding.last_order = new_order
        else:
            # 기타 레벨에서는 정순으로 다음 순서의 그림을 가져옴
            new_order = (user_proceeding.last_order + 1) % picture_number_by_level[level]
            user_proceeding.last_order = new_order
    else:
        # is_order가 거짓일 때: 랜덤으로 그림을 선택하는 로직
        all_pictures = list(BasePictures.objects.filter(level=picture_level).values_list('order', flat=True))
        seen_pictures = user_proceeding.seen_pictures or []
        available_pictures = [order for order in all_pictures if order not in seen_pictures]
        
        # 모든 그림을 본 경우, 본 그림 목록을 리셋하여 다시 선택할 수 있게 함
        if not available_pictures:
            seen_pictures = []  # 이미 본 그림 목록 리셋
            available_pictures = all_pictures

        # 랜덤으로 그림을 선택
        chosen_order = random.choice(available_pictures)
        user_proceeding.last_order = chosen_order
        seen_pictures.append(chosen_order)
        user_proceeding.seen_pictures = seen_pictures


    # 선택된 그림을 데이터베이스에서 가져옴
    picture = BasePictures.objects.get(level=picture_level, order=user_proceeding.last_order)
    # 그림의 URL과 순서를 JSON 형태로 반환
    return picture



def fetch_altered_level_base_picture(request, user_accuracy, user_proceeding):
    # 사용자가 이전에 클리어한 레벨이면 is_order=false // 아니면 true
    user_proceeding.is_order = False if user_proceeding.level in user_proceeding.clear_level else True

    if user_proceeding.is_order:
        if user_proceeding.level <= 2:
            # 레벨 0, 1, 2는 0번 그림부터 시작
            user_proceeding.last_order = 0
        else: # 레벨 3, 4는 마지막 그림부터 시작
            user_proceeding.last_order = picture_number_by_level[user_proceeding.level]-1
    else:
        # 레벨에 맞춰 범위 중에 하나의 그림 선택
        user_proceeding.last_order = random.randrange(picture_number_by_level[user_proceeding.level])          
    # 본 그림 목록 초기화
    user_proceeding.seen_pictures = []
    
    # 사용자 정확도 정보 초기화
    user_accuracy.successive_correct = 0
    user_accuracy.successive_wrong = 0

    # 새 레벨과 last_order에 기반하여 이미지 URL 가져오기
    picture_level = user_proceeding.level if user_proceeding.level <= 2 else user_proceeding.level - 2
    picture = BasePictures.objects.filter(level=picture_level, order=user_proceeding.last_order).first()

    # seen_pictures에 현재 last_order를 추가하고 저장
    user_proceeding.seen_pictures.append(user_proceeding.last_order)  # seen_pictures에 추가
    user_proceeding.save()

    return picture



# 난이도 자동 조정 구현 테스트 필요    
@csrf_exempt
def check_change_level(request, user_accuracy, user_proceeding):
    data = json.loads(request.body)
    accuracy = data.get('accuracy', 0)
    level_changed = False
    if accuracy >= 0.6:
        user_accuracy.successive_correct += 1
        user_accuracy.successive_wrong = 0
    elif accuracy < 0.2:
        user_accuracy.successive_wrong += 1
        user_accuracy.successive_correct = 0
    else:
        user_accuracy.successive_correct = user_accuracy.successive_wrong = 0

    if user_accuracy.successive_correct >= 3:
        if user_proceeding.level not in user_proceeding.clear_level:
            user_proceeding.clear_level.append(user_proceeding.level)
        if user_proceeding.level < 4:
            user_proceeding.level += 1
            level_changed = 1
        user_accuracy.successive_correct = 0
    elif user_accuracy.successive_wrong >= 2:
        if user_proceeding.level > 0:
            user_proceeding.level -= 1
            level_changed = -1
        user_accuracy.successive_wrong = 0

    return level_changed
