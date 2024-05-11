from django.urls import path
from .views import picture_func, get_picture

urlpatterns = [
    path('', picture_func),
    path('request/', get_picture, name='get_picture'),
]
