from lms import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home-page'),
    path('meus-cursos/', views.my_courses, name='my-courses'),
    path('cadastrar-curso/', views.create_course, name='create-course'),
    path('editar-curso/', views.create_course, name='edit-course'),
]
