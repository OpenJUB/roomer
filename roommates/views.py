from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required


from roomer.models import RoommateRequest, UserProfile
from .forms import RequestRoommateForm


@login_required
def overview(request, form=RequestRoommateForm(), mutual_request=False, different_colleges=False):
    context = {
        'form': form,
        'mutual_request': mutual_request,
        'different_colleges': different_colleges
    }

    return render(request, 'roommates/overview.html', context)


@require_GET
@login_required
def deny(request, request_id):
    req = get_object_or_404(RoommateRequest, pk=request_id)
    req.delete()

    return redirect('roommate-overview')


@require_GET
@login_required
def accept(request, request_id):
    req = get_object_or_404(RoommateRequest, pk=request_id)
    req.accept()

    return redirect('roommate-overview')


@require_POST
@login_required
def invite(request):
    form = RequestRoommateForm(request.POST)

    if form.is_valid():
        other = UserProfile.objects.get(username=form.cleaned_data['receiver'])
        code = request.user.send_roommate_request(other)

        if code != UserProfile.REQUEST_SENT:
            return overview(
                request,
                mutual_request=(code == UserProfile.REQUEST_MUTUAL),
                different_colleges=(code == UserProfile.REQUEST_INVALID))
        else:
            return overview(request)

    return overview(request, form=form)


@require_GET
@login_required
def remove(request, roommate_id):
    mate = get_object_or_404(UserProfile, pk=roommate_id)
    request.user.remove_roommate(mate)

    return redirect('roommate-overview')