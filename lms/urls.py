from lms import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home-page'),
    path('meus-cursos/', views.my_courses, name='my-courses'),
]
