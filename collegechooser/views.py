import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render

from .models import UpdateWindow

# Create your views here.
@require_GET
def overview(request):
    now = datetime.datetime.now()
    profile = request.user

    # Get currently active phase
    windows = UpdateWindow.objects.filter(start__lte=now, end__gt=now).order_by('-start')
    current_window = windows.first()

    context = {
        'window': current_window,
        'profile': profile
    }

    if current_window:
        context['can_change_college'] = current_window.can_update_colleges(profile)
    else:
        context['can_change_college'] = False

    return render(request, 'overview.html', context)
