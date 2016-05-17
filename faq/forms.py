from django.forms import ModelForm

from .models import Question


class QuestionAddForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']
