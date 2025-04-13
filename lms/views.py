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
