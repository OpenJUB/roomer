__author__ = 'leonhard'

from django.shortcuts import render

from collegechooser.utils import get_next_phases

def home(request):

    return render(request, 'base.html', {'phases': get_next_phases(request.user)})