from django.urls import path
from . import views

urlpatterns = [
    path('', views.load_base_picture),
    path('test/', views.test_picture_load),
    path('new/', views.change_base_picture),
    path('request/', views.get_picture, name='get_picture'),
    path('adjust-level/', views.adjust_level, name='adjust-level'),
    path('adjust-level-with-accuracy', views.adjust_level_with_accuracy, name='adjust-level-with-accuracy')
]
