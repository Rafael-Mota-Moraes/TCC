from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def validate_mp4_extension(value):
    if not value.name.lower().endswith(".mp4"):
        raise ValidationError("Apenas arquivos MP4 são permitidos")


def validate_pdf_extension(value):
    if not value.name.lower().endswith(".pdf"):
        raise ValidationError("Apenas arquivos PDF são permitidos")


def get_video_mime_type(filename):
    extension = filename.split(".")[-1].lower()
    return {
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mkv": "video/x-matroska",
    }.get(extension, "video/mp4")


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
        "Course",
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
        validators=[validate_mp4_extension],
        null=True,
        blank=True,
    )

    document_content = models.FileField(
        verbose_name="Conteúdo em vídeo",
        upload_to="lectures/documents/",
        validators=[validate_pdf_extension],
        null=True,
        blank=True,
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

    def get_video_mime_type(self):
        return get_video_mime_type(self.video_content.name)


class Comment(models.Model):
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    content = models.TextField(
        verbose_name="O comentário",
        blank=True,
        null=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)


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


class UserLecturesRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    course = models.ForeignKey(
        Course,
        related_name="course_lecture_user_relation",
        on_delete=models.CASCADE,
        verbose_name="Curso",
        null=True,
    )
    is_concluded = models.BooleanField(default=False)
