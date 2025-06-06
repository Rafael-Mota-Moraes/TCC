# views.py

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, ExpressionWrapper, F, FloatField, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import (
    Comment,
    Course,
    Lecture,
    UserCourseRegistration,
    UserLecturesRelation,
)


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
            document_content = request.FILES.get("document_content")

            have_content = video_content or document_content

            if not title or not have_content:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Título e vídeo ou documento são obrigatórios",
                    }
                )

            next_order = Lecture.objects.filter(course=course).count()

            lecture = Lecture.objects.create(
                course=course,
                title=title,
                video_content=video_content,
                document_content=document_content,
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
        document_content = request.FILES.get("document_content")

        have_content = video_content or document_content

        if not title or not have_content:
            messages.error(request, "Título e vídeo são obrigatórios")
            return redirect("edit-course", course_id=course_id)

        next_order = Lecture.objects.filter(course=course).count()

        Lecture.objects.create(
            course=course,
            title=title,
            video_content=video_content,
            document_content=document_content,
            order=next_order,
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
            "document_url": lecture.document_content.url
            if lecture.document_content
            else None,
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


@login_required
def course_stats(request, course_id):
    course = get_object_or_404(Course, id=course_id, belongs_to=request.user)

    total_lectures = course.lectures.count()
    total_registrations = course.course_registration.count()

    total_completions = UserLecturesRelation.objects.filter(
        course=course, is_concluded=True
    ).count()

    per_user = (
        UserLecturesRelation.objects.filter(course=course)
        .values("user", "user__username")
        .annotate(
            concluidos=Count("lecture", filter=Q(is_concluded=True)),
            total=Count("lecture"),
        )
        .annotate(
            pct=ExpressionWrapper(
                F("concluidos") * 100.0 / F("total"), output_field=FloatField()
            )
        )
    )

    full_completion_count = per_user.filter(concluidos=total_lectures).count()

    avg_pct = (
        per_user.aggregate(media=Sum("pct") / Count("user"))["media"]
        if total_registrations
        else 0
    )

    per_lecture = Lecture.objects.filter(course=course).annotate(
        concluidos=Count(
            "userlecturesrelation", filter=Q(userlecturesrelation__is_concluded=True)
        ),
        pct=ExpressionWrapper(
            F("concluidos") * 100.0 / total_registrations, output_field=FloatField()
        )
        if total_registrations
        else 0,
    )

    context = {
        "course": course,
        "total_lectures": total_lectures,
        "total_registrations": total_registrations,
        "total_completions": total_completions,
        "full_completion_count": full_completion_count,
        "avg_completion_rate": round(avg_pct, 2),
        "lecture_stats": per_lecture,
        "user_stats": per_user,
    }

    return render(request, "lms/stats-course.html", context)


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
    course = Course.objects.get(id=course_id)

    is_enrolled = UserCourseRegistration.objects.filter(
        user=request.user, course=course
    ).exists()

    if not is_enrolled:
        messages.error(request, "Você não está matriculado neste curso.")
        return redirect("courses_list")

    lectures = Lecture.objects.filter(course=course).order_by("order")
    lecture_id = request.GET.get("lecture", None)
    try:
        if lecture_id:
            current_lecture = lectures.get(id=lecture_id)
        else:
            current_lecture = lectures.first()
    except (Lecture.DoesNotExist, AttributeError):
        current_lecture = None

    current_lecture = None
    if lecture_id:
        try:
            current_lecture = lectures.get(id=lecture_id)
        except Lecture.DoesNotExist:
            if lectures.exists():
                current_lecture = lectures.first()
    elif lectures.exists():
        current_lecture = lectures.first()

    lecture_progress = {}
    completed_lectures = 0

    for lecture in lectures:
        user_lecture, created = UserLecturesRelation.objects.get_or_create(
            user=request.user,
            lecture=lecture,
            course=course,
            defaults={"is_concluded": False},
        )
        lecture_progress[lecture.id] = user_lecture.is_concluded

        if user_lecture.is_concluded:
            completed_lectures += 1

    comments = (
        Comment.objects.filter(lecture=current_lecture, parent__isnull=True)
        .select_related("posted_by")
        .prefetch_related("replies")
        .order_by("-id")
        if current_lecture
        else []
    )

    context = {
        "course": course,
        "lectures": lectures,
        "current_lecture": current_lecture,
        "lecture_progress": lecture_progress,
        "completed_lectures": completed_lectures,
        "comments": comments,
    }

    return render(request, "lms/watch-course.html", context=context)


@login_required
@require_POST
def update_lecture_progress(request):
    try:
        data = json.loads(request.body)
        lecture_id = data.get("lecture_id")
        is_concluded = data.get("is_concluded", False)

        lecture = Lecture.objects.get(id=lecture_id)

        relation, created = UserLecturesRelation.objects.update_or_create(
            user=request.user,
            lecture=lecture,
            course=lecture.course,
            defaults={"is_concluded": is_concluded},
        )

        return JsonResponse(
            {
                "success": True,
                "lecture_id": lecture_id,
                "is_concluded": relation.is_concluded,
            }
        )
    except Lecture.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Aula não encontrada"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_POST
def add_comment(request):
    user = request.user if request.user.is_authenticated else None
    content = request.POST.get("content")
    lecture_id = request.POST.get("lecture_id")
    parent_id = request.POST.get("parent_id")

    if not content or not lecture_id:
        return redirect(request.META.get("HTTP_REFERER", "/"))

    lecture = Lecture.objects.get(id=lecture_id)
    parent = Comment.objects.get(id=parent_id) if parent_id else None

    Comment.objects.create(
        posted_by=user,
        content=content,
        lecture=lecture,
        parent=parent,
    )
    return redirect(request.META.get("HTTP_REFERER", "/"))
