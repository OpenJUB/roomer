from django.shortcuts import render

from .utils import get_points_breakdown
from roomer.utils import get_next_phases


# For stats
from allocation.utils import get_college_fills, get_fill_percentages
from faq import models as faq_models
from roomer import models as roomer_models


def home(request):
    return render(request, 'base.html', {
        'phases': get_next_phases(request.user),
        'points': get_points_breakdown(request.user)
    })


def stats(request):
    context = {
        'fills': get_college_fills(),
        'percentage_fills': get_fill_percentages(),
        'faq_count': faq_models.Question.objects.count(),
        'user_count': roomer_models.UserProfile.objects.count()
    }

    return render(request, 'roomer/stats.html', context)
