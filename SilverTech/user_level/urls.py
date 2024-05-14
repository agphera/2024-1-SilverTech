from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_picture_load),
    path('picture-training/', views.picture_training),
    path('fetch-picture/', views.fetch_picture),
    path('adjust-level-with-accuracy', views.adjust_level_with_accuracy, name='adjust-level-with-accuracy')
]
