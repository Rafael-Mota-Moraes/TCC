from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    belongs_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title = models.CharField(
        verbose_name="Título do curso",
        max_length=255,
        blank=False,
        null=False,
    )
    description = models.TextField(
        verbose_name="Descrição do curso",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Atualizado em",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Lecture(models.Model):
    course = models.ForeignKey(
        Course,
        related_name="lectures",
        on_delete=models.CASCADE,
        verbose_name="Curso",
        null=True,
    )
    title = models.CharField(
        verbose_name="Título da aula",
        max_length=255,
        blank=False,
        null=False,
    )
    video_content = models.FileField(
        verbose_name="Conteúdo em vídeo",
        upload_to="lectures/videos/",
    )
    order = models.PositiveIntegerField(
        verbose_name="Ordem",
        default=0,
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class UserCourseRegistration(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    course = models.ForeignKey(
        Course,
        related_name="course_registration",
        on_delete=models.CASCADE,
        verbose_name="Curso",
        null=True,
    )
