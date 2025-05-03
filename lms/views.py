# views.py

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Course, Lecture, UserCourseRegistration, UserLecturesRelation


def home(request):
    courses = Course.objects.all()

    return render(request, "lms/home.html", {"courses": courses})


@login_required
def my_courses(request):
    courses = Course.objects.filter(belongs_to=request.user)

    registered_courses = UserCourseRegistration.objects.filter(user=request.user)

    return render(
        request,
        "lms/my-courses.html",
        {"courses": courses, "registered_courses": registered_courses},
    )


@login_required
def create_course(request):
    if request.method == "POST":
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            try:
                title = request.POST.get("title")
                description = request.POST.get("description")

                if not title:
                    return JsonResponse(
                        {"success": False, "error": "O título do curso é obrigatório"}
                    )

                course = Course.objects.create(
                    title=title, description=description, belongs_to=request.user
                )

                return JsonResponse(
                    {
                        "success": True,
                        "course_id": course.id,
                        "message": "Curso criado com sucesso!",
                    }
                )
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
        else:
            title = request.POST.get("title")
            description = request.POST.get("description")

            if not title:
                messages.error(request, "O título do curso é obrigatório")
                return redirect("create-course")

            Course.objects.create(
                title=title, description=description, belongs_to=request.user
            )

            messages.success(request, "Curso criado com sucesso!")
            return redirect("my-courses")

    return render(request, "lms/create-course.html")


@login_required
@require_POST
def add_lecture(request, course_id):
    course = get_object_or_404(Course, id=course_id, belongs_to=request.user)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            title = request.POST.get("title")
            video_content = request.FILES.get("video_content")

            if not title or not video_content:
                return JsonResponse(
                    {"success": False, "error": "Título e vídeo são obrigatórios"}
                )

            next_order = Lecture.objects.filter(course=course).count()

            lecture = Lecture.objects.create(
                course=course,
                title=title,
                video_content=video_content,
                order=next_order,
            )

            return JsonResponse(
                {
                    "success": True,
                    "lecture_id": lecture.id,
                    "message": "Aula adicionada com sucesso!",
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        title = request.POST.get("title")
        video_content = request.FILES.get("video_content")

        if not title or not video_content:
            messages.error(request, "Título e vídeo são obrigatórios")
            return redirect("edit-course", course_id=course_id)

        next_order = Lecture.objects.filter(course=course).count()

        Lecture.objects.create(
            course=course, title=title, video_content=video_content, order=next_order
        )

        messages.success(request, "Aula adicionada com sucesso!")
        return redirect("edit-course", course_id=course_id)


@login_required
def get_course_lectures(request, course_id):
    course = get_object_or_404(Course, id=course_id, belongs_to=request.user)
    lectures = Lecture.objects.filter(course=course).order_by("order")

    lectures_data = [
        {
            "id": lecture.id,
            "title": lecture.title,
            "order": lecture.order,
            "video_url": lecture.video_content.url if lecture.video_content else None,
        }
        for lecture in lectures
    ]

    return JsonResponse({"success": True, "lectures": lectures_data})


@login_required
@require_POST
def reorder_lectures(request, course_id):
    course = get_object_or_404(Course, id=course_id, belongs_to=request.user)

    try:
        data = json.loads(request.body)
        lectures_order = data.get("lectures", [])

        for item in lectures_order:
            lecture_id = item.get("id")
            order = item.get("order")

            lecture = get_object_or_404(Lecture, id=lecture_id, course=course)
            lecture.order = order
            lecture.save()

        return JsonResponse(
            {"success": True, "message": "Ordem das aulas atualizada com sucesso!"}
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_POST
def delete_lecture(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id, course__belongs_to=request.user)
    course = lecture.course

    try:
        lecture.delete()

        remaining_lectures = Lecture.objects.filter(course=course).order_by("order")
        for index, lec in enumerate(remaining_lectures):
            lec.order = index
            lec.save()

        return JsonResponse({"success": True, "message": "Aula excluída com sucesso!"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, belongs_to=request.user)
    lectures = Lecture.objects.filter(course=course).order_by("order")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if not title:
            messages.error(request, "O título do curso é obrigatório")
            return redirect("edit-course", course_id=course_id)

        course.title = title
        course.description = description
        course.save()

        messages.success(request, "Curso atualizado com sucesso!")
        return redirect("my-courses")

    context = {"course": course, "lectures": lectures}
    return render(request, "lms/edit-course.html", context)


def course_infos(request, course_id):
    course = Course.objects.filter(id=course_id).first()
    lectures = Lecture.objects.filter(course=course).order_by("order")

    registered = UserCourseRegistration.objects.filter(
        user=request.user, course=course
    ).first()

    is_registered = True if registered else False

    context = {"course": course, "lectures": lectures, "is_registered": is_registered}
    return render(request, "lms/course-infos.html", context)


def register_in_course(request, course_id):
    try:
        course = Course.objects.filter(id=course_id).first()
        registration = UserCourseRegistration(
            user=request.user,
            course=course,
        )
        registration.save()

        course_lectures = Lecture.objects.filter(course=course)

        for lecture in course_lectures:
            new_user_lecture_relation = UserLecturesRelation(
                user=request.user, lecture=lecture, course=course
            )
            new_user_lecture_relation.save()

        messages.success(
            request=request,
            message=f"Parabéns! Você está matriculado no curso {course.title}",
        )

        return redirect("my-courses")
    except Exception:
        messages.error(
            request=request,
            message="Ocorreu algum erro, tente novamente",
        )
        return redirect("home-page")


def watch_course(request, course_id):
    context = {}
    return render(request, "lms/watch-course.html", context=context)
