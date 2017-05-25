import datetime

from django.views.decorators.http import require_http_methods, require_GET
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.conf import settings
from django.utils import timezone

from .models import Phase, RoomPhase
from roomer.models import UserPreference, Room
from .forms import RoomPrefForm
from .utils import *


@require_http_methods(['POST', 'GET'])
@login_required
def list_preferences(request):
    users = list(request.user.roommates.all()) + [request.user]

    prefs = UserPreference.objects.filter(user__in=users).order_by(
        'preference_level')

    if request.method == 'POST':
        form = RoomPrefForm(request.POST, user=request.user)

        if form.is_valid():
            room = Room.objects.get(code=form.cleaned_data.get('room_code'))
            lowest_request = UserPreference.objects.filter(
                user=request.user).order_by('-preference_level').first()

            if not lowest_request:
                lowest_pref = 1
            else:
                lowest_pref = lowest_request.preference_level + 1

            UserPreference.objects.create(user=request.user, room=room,
                                          preference_level=lowest_pref)

            return redirect('room-request-overview')
    else:
        form = RoomPrefForm(None, user=request.user)

    context = {
        'preferences': prefs,
        'can_apply': RoomPhase.objects.get_current() is not None,
        'form': form
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


@require_GET
@login_required
def room_code_autocomplete(request):
    current_phase = RoomPhase.objects.get_current()

    # Return no rooms when there is no allocation being done
    if current_phase is None or request.user.is_anonymous():
        return JsonResponse([], safe=False)

    # Get all free rooms (for perf reasons)
    qs = Room.objects.filter(assigned_user__isnull=True,
                             college=request.user.college).order_by('code')

    # Filter by room code if given
    if 'q' in request.GET:
        qs = qs.filter(code__istartswith=request.GET['q'])

    room_result = []

    # Filter rooms that are not being allocated
    for room in qs:
        avail, reason = current_phase.is_allocating_room(room)

        room_result.append({
            'code': room.code,
            'available': avail,
            'applicants': max(0, room.applicants.exclude(
                user=request.user).count()),
            'reason': reason
        })

    # Sort by availability
    rooms = sorted(room_result, key=lambda r: r['available'], reverse=True)

    return JsonResponse(rooms[:10], safe=False)


@require_GET
@login_required
def room_results(request):
    context = {
        'allocations': [
            {
                'name': n,
                'rooms': Room.objects.filter(college=p).exclude(assigned_user=None).order_by('code')
            } for (p, n) in settings.COLLEGE_CHOICES
        ]
    }

    return render(request, 'allocation/results.html', context=context)
