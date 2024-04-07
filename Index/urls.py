from django.urls import path
from .views import send_audio_to_naver_stt

urlpatterns = [
    path('send_audio/', send_audio_to_naver_stt, name='send_audio_to_naver_stt'),
]
