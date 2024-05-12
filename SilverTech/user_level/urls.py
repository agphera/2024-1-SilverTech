from django.urls import path
from .views import load_base_picture, test_picture_load, change_base_picture,get_picture

urlpatterns = [
    path('', load_base_picture),
    path('test/', test_picture_load),
    path('new/', change_base_picture),
    path('request/', get_picture, name='get_picture')
]
