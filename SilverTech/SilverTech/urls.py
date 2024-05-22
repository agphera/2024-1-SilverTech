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
from myapp1.views import index, second_page ,send_audio_to_naver_stt  # 'index' 뷰도 임포트합니다.
from myapp1.views import proxy_to_naver_stt, make_pic_karlo
from myapp1.views import upload_image

urlpatterns = [
    path('', index, name='index'),  # 직접 임포트된 'index' 뷰를 사용합니다.
    path('second_page', second_page, name = 'second_page'),
    path('api/naver-stt/', proxy_to_naver_stt, name='naver_stt_proxy'),
    path('func/make-pic/', make_pic_karlo, name='make_pic_karlo'),
    path('image/', upload_image, name='upload_image')
]
