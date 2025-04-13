# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Course, Module, Lecture


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

    title = forms.CharField(
        label='Título do curso',
        widget=forms.TextInput(
            attrs={'class': 'input'})
    )


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']

    order = forms.IntegerField(widget=forms.HiddenInput())


class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'video_content', 'order']

    order = forms.IntegerField(widget=forms.HiddenInput())


# Formsets
ModuleFormSet = inlineformset_factory(
    Course, Module, form=ModuleForm, extra=1, can_order=True, can_delete=True, min_num=1, validate_min=True
)

LectureFormSet = inlineformset_factory(
    Module, Lecture, form=LectureForm, extra=1, can_order=True, can_delete=True, min_num=1, validate_min=True
)
