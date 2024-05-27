"""
URL configuration for SilverTech project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.urls import path


from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from myapp1.views import index, Camera, StartingPage, send_audio_to_naver_stt, login_capture, login_order # 'index' 뷰도 임포트합니다.
from django.contrib import admin
from django.urls import include, path
from myapp1.views import proxy_to_naver_stt, make_pic_karlo, load_base_picture,upload_image, fetch_user_info

schema_view = get_schema_view( # Swagger
    openapi.Info(
        title="OSS API",  # 원하는 제목 작성
        default_version='v1',  # 애플리케이션의 버전
        description="Test description",  # 설명
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
#    authentication_classes=[]  # settings.py의 REST_FRAMEWORK > DEFAULT_AUTHENTICTION_CLASSES 가 적용되어 있다면 추가해줄 것
)


urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    path('', StartingPage, name='StartingPage'),  # 직접 임포트된 'index' 뷰를 사용합니다.
    path('Camera',Camera,name='Camera'), 

    path('index',index, name='index'), #

    #path('',index, name='index'),
    #path('StartingPage',StartingPage,name='StartingPage'),
    path('api/naver-stt/', proxy_to_naver_stt, name='naver_stt_proxy'),
    path('func/make-pic/', make_pic_karlo, name='make_pic_karlo'),
    path('picture-load/', include('user_level.urls')),
    path('image/', upload_image, name='upload_image'),
    path('login_capture/', login_capture, name='login_capture'),
    path('login_order/', login_order, name='login_order')
    ]
