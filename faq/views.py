from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Question
from .forms import QuestionAddForm

@login_required
def home(request):
    return render(request, 'faq/home.html', {
        'question_list': Question.objects.filter(published=True) | Question.objects.filter(creator=request.user)
    })


@login_required
def add(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = QuestionAddForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            q = form.save(commit=False)
            q.creator = request.user
            q.save()

            # redirect to a new URL:
            return redirect('question-home')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = QuestionAddForm()

    return render(request, 'faq/add.html', {'form': form})