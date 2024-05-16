from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_picture_load),
    path('picture-training/', views.login_to_training),
    path('fetch-picture/', views.load_next_base_picture),
    path('adjust-level-with-accuracy', views.check_change_level, name='adjust-level-with-accuracy')
]
