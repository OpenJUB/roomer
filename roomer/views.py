__author__ = 'leonhard'

from django.shortcuts import render

from .utils import get_points_breakdown
from roomer.utils import get_next_phases


def home(request):
    return render(request, 'base.html', {
        'phases': get_next_phases(request.user),
        'points': get_points_breakdown(request.user)
    })