from .forms import CourseForm, ModuleForm, LectureForm
from .models import Course, Module, Lecture
from django.forms import inlineformset_factory
from .forms import CourseForm, ModuleFormSet, LectureFormSet
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course
# Create your views here.


def home(request):
    return render(request, 'lms/home.html')


@login_required
def my_courses(request):
    courses = Course.objects.filter(belongs_to=request.user)

    return render(request, 'lms/my-courses.html', {'courses': courses})


@login_required
@login_required
def create_course(request):
    # Inicialize estas variáveis no escopo principal da função
    course_form = None
    module_formset = None

    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES)

        if course_form.is_valid():
            try:
                course = course_form.save(commit=False)
                try:
                    course.belongs_to = request.user
                    course.save()
                except Exception as e:
                    print(f"Aviso: Não foi possível definir belongs_to: {e}")
                    from django.db import connection
                    cursor = connection.cursor()
                    cursor.execute(
                        "INSERT INTO lms_course (title, description, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'))",
                        [course.title, course.description]
                    )
                    cursor.execute("SELECT last_insert_rowid()")
                    course_id = cursor.fetchone()[0]
                    course.id = course_id

                module_formset = ModuleFormSet(request.POST, instance=course)

                if module_formset.is_valid():
                    modules = module_formset.save(commit=False)

                    for module in modules:
                        module.course_id = course.id
                        module.save()

                    for i, module in enumerate(modules):
                        module_prefix = f"{module_formset.prefix}-{i}"
                        lecture_data = {}

                        for key, value in request.POST.items():
                            if key.startswith(f"{module_prefix}-lecture-") and "-title" in key:
                                lecture_index = key.split(
                                    "-lecture-")[1].split("-")[0]
                                lecture_prefix = f"{module_prefix}-lecture-{lecture_index}"

                                if lecture_prefix not in lecture_data:
                                    lecture_data[lecture_prefix] = {}

                                for field_key, field_value in request.POST.items():
                                    if field_key.startswith(lecture_prefix):
                                        field_name = field_key.replace(
                                            f"{lecture_prefix}-", "")
                                        lecture_data[lecture_prefix][field_name] = field_value

                        for key, file in request.FILES.items():
                            if key.startswith(f"{module_prefix}-lecture-"):
                                lecture_prefix = "-".join(key.split("-")[:4])
                                field_name = key.replace(
                                    f"{lecture_prefix}-", "")

                                if lecture_prefix in lecture_data:
                                    lecture_data[lecture_prefix][field_name] = file

                        for lecture_prefix, lecture_fields in lecture_data.items():
                            if 'title' in lecture_fields and lecture_fields['title']:
                                lecture = Lecture(
                                    module=module,
                                    title=lecture_fields.get('title', ''),
                                    order=lecture_fields.get('order', 0)
                                )

                                if 'video_content' in lecture_fields:
                                    lecture.video_content = lecture_fields['video_content']

                                lecture.save()

                return redirect('course_list')
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f"Erro ao salvar o curso: {str(e)}")

                if not module_formset:
                    module_formset = ModuleFormSet()
                    for module_form in module_formset:
                        module_form.nested = []
        else:
            module_formset = ModuleFormSet(request.POST)
            for module_form in module_formset:
                module_form.nested = []
    else:
        course_form = CourseForm()
        module_formset = ModuleFormSet()

        for module_form in module_formset:
            module_form.nested = []

    if not course_form:
        course_form = CourseForm()

    if not module_formset:
        module_formset = ModuleFormSet()
        for module_form in module_formset:
            module_form.nested = []

    return render(request, 'lms/new-course.html', {
        'course_form': course_form,
        'module_formset': module_formset,
    })
