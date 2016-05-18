from django.utils import timezone

from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import UpdateWindow
from .forms import CollegePrefForm
from .utils import *

@require_http_methods(['POST', 'GET'])
@login_required
def overview(request):
    now = timezone.now()
    profile = request.user

    # Get currently active phase
    windows = UpdateWindow.objects.filter(start__lte=now, end__gt=now).order_by('end')
    current_window = windows.first()

    context = {
        'window': current_window,
        'profile': profile,
        'max_percentage': settings.MAX_COLLEGE_FILL
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
        elif current_window.live_allocation:
            new_college = request.POST.get('college', default='')

            if new_college in settings.COLLEGE_CODES:
                if not is_full(new_college):
                    profile.college = new_college
                    profile.save()
                else:
                    context['error'] = 'The selected college is full.'
            else:
                context['error'] = 'You filthy hacker.'
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

    fills = get_fill_percentages()
    college_choices = [(code, display, fills.get(code, 0)) for code, display in settings.COLLEGE_CHOICES]

    context['college_choices'] = college_choices

    colleges = []
    for choice in settings.COLLEGE_CHOICES + [('', 'Unallocated')]:
        colleges.append({
            'name': choice[1],
            'users': UserProfile.objects.filter(college=choice[0]).order_by('first_name', 'last_name')
        })

    context['colleges'] = colleges
    context['codes'] = settings.COLLEGE_CHOICES,

    return render(request, 'overview.html', context)
