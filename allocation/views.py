import datetime

from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.conf import settings
from django.utils import timezone

from .models import Phase, CollegePhase, RoomPhase
from roomer.models import UserPreference, Room
from .forms import  RoomPrefForm
from .utils import *


@require_http_methods(['POST', 'GET'])
@login_required
def list_preferences(request):
    users = list(request.user.roommates.all()) + [request.user]

    prefs = UserPreference.objects.filter(user__in=users).order_by('preference_level')

    context = {
        'preferences': prefs
    }

    return render(request, 'allocation/overview.html', context=context)

@login_required
def preference_up(request, pref_id):
    preference = get_object_or_404(UserPreference, pk=pref_id)

    if preference.can_edit(request.user):
        preference.move_up()

    return redirect('room-request-overview')

@login_required
def preference_down(request, pref_id):
    preference = get_object_or_404(UserPreference, pk=pref_id)

    if preference.can_edit(request.user):
        preference.move_down()

    return redirect('room-request-overview')

@login_required
def remove_preference(request, pref_id):
    preference = get_object_or_404(UserPreference, pk=pref_id)

    if preference.can_edit(request.user):
        preference.delete()

    return redirect('room-request-overview')

@login_required
def apply_for_room(request):
    if request.method == 'POST':
        form = RoomPrefForm(request.POST, user=request.user)

        if form.is_valid():
            room = Room.objects.get(code=form.cleaned_data.get('room_code'))
            lowest_request = UserPreference.objects.filter(user=request.user).order_by('-preference_level').first()

            if not lowest_request:
                lowest_pref = 1
            else:
                lowest_pref = lowest_request.preference_level + 1

            UserPreference.objects.create(user=request.user, room=room, preference_level=lowest_pref)

            return redirect('room-request-overview')
    else:
        form = RoomPrefForm(None, user=request.user)

    return render(request, 'allocation/add.html', context={'form': form})
