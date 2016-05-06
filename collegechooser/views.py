import datetime

from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import UpdateWindow
from .forms import CollegePrefForm


@require_http_methods(['POST', 'GET'])
@login_required
def overview(request):
    now = datetime.datetime.now()
    profile = request.user

    # Get currently active phase
    windows = UpdateWindow.objects.filter(start__lte=now, end__gt=now).order_by('end')
    current_window = windows.first()

    context = {
        'window': current_window,
        'profile': profile
    }

    if current_window:
        context['can_change_college'] = current_window.can_update_colleges(profile)
    else:
        context['can_change_college'] = False

    if request.method == 'POST' and current_window and current_window.is_open():
        if request.POST.get('stay', default=False):
            if profile.college == '' and profile.old_college != '':
                profile.college = profile.old_college
                profile.save()
                return redirect(overview)
        else:
            form = CollegePrefForm(request.POST)

            if form.is_valid():
                profile.college_pref = form.to_pref_string()
                profile.save()

            context['pref_form'] = form
    else:
        if context['can_change_college']:
            form = CollegePrefForm.from_pref_string(profile.college_pref)
            context['pref_form'] = form

    return render(request, 'overview.html', context)
