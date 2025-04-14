# urls.py

from django.urls import path

from lms import views

urlpatterns = [
    path("", views.home, name="home-page"),
    path("meus-cursos/", views.my_courses, name="my-courses"),
    path("criar-curso/", views.create_course, name="create-course"),
    path("editar-curso/<int:course_id>/", views.edit_course, name="edit-course"),
    path("adicionar-aula/<int:course_id>/", views.add_lecture, name="add-lecture"),
    path(
        "aulas-curso/<int:course_id>/",
        views.get_course_lectures,
        name="course-lectures",
    ),
    path(
        "reordenar-aulas/<int:course_id>/",
        views.reorder_lectures,
        name="reorder-lectures",
    ),
    path("excluir-aula/<int:lecture_id>/", views.delete_lecture, name="delete-lecture"),
]
