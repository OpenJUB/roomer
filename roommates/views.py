import random

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings

from roomer.models import RoommateRequest, UserProfile
from roomer.utils import make_freshie, has_freshie
from .forms import RequestRoommateForm

from notify.utils import InboxNotification


@login_required
def overview(request, form=RequestRoommateForm(), mutual_request=False, different_colleges=False):
    context = {
        'form': form,
        'mutual_request': mutual_request,
        'different_colleges': different_colleges,
        'can_change_roommates': request.user.can_change_roommates(),
        'can_add_freshman': not has_freshie(request.user.username),
        'freshman_invite': random.choice(["freshie", "freshman please", "I want a freshie"])
    }

    return render(request, 'roommates/overview.html', context)


@require_GET
@login_required
def deny(request, request_id):
    req = get_object_or_404(RoommateRequest, pk=request_id)
    if req.receiver == request.user:
        req.delete()

    return redirect('roommate-overview')


@require_GET
@login_required
def accept(request, request_id):
    req = get_object_or_404(RoommateRequest, pk=request_id)
    if req.receiver == request.user:
        req.accept()

    return redirect('roommate-overview')


@require_POST
@login_required
def invite(request):
    form = RequestRoommateForm(request.POST)

    if form.is_valid():
        other = UserProfile.objects.get(username=form.cleaned_data['receiver'])
        code, new_request = request.user.send_roommate_request(other)

        if code != UserProfile.REQUEST_SENT:
            return overview(
                request,
                mutual_request=(code == UserProfile.REQUEST_MUTUAL),
                different_colleges=(code == UserProfile.REQUEST_INVALID))
        else:
            InboxNotification(new_request).send()
            return overview(request)

    return overview(request, form=form)


@require_GET
@login_required
def invite_freshman(request):
    request.user.roommates.add(make_freshie(request.user.username))

    return redirect('roommate-overview')


@require_GET
@login_required
def remove(request, roommate_id):
    mate = get_object_or_404(UserProfile, pk=roommate_id)

    request.user.remove_roommate(mate)

    if mate.username == settings.FRESHIE_USERNAME + '-' + request.user.username:
        mate.delete()

    return redirect('roommate-overview')


@require_GET
@login_required
def autocomplete(request):
    qs = UserProfile.objects.filter(college=request.user.college)

    if 'q' in request.GET:
        q = request.GET['q']
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q))

    values = qs.values_list('username', flat=True)

    return JsonResponse(list(values), safe=False)
