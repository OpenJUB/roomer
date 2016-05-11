from django.utils import timezone

from django.conf import settings
from django.db.models import Count

from collegechooser.models import UpdateWindow
from allocation.models import RoomPhase

from roomer.models import UserProfile

from babel.dates import format_timedelta


def get_college_capacity(college_code):
    for code, capacity in settings.COLLEGE_CAPACITIES:
        if college_code == code:
            return capacity

    return 0


def is_full(college_code):
    if college_code not in settings.COLLEGE_CODES:
        return True

    fills = get_college_fills()
    capacity = get_college_capacity(college_code)

    return fills.get(college_code, 0) >= ((capacity * settings.MAX_COLLEGE_FILL) / 100)


def can_allocate_to(college_code):
    return not is_full(college_code)


def get_college_fills():
    raw_fills = UserProfile.objects.values('college').annotate(count=Count('college'))

    return {fill['college']: fill['count'] for fill in raw_fills}


def get_fill_percentages():
    fills = get_college_fills()

    out = {code: (fills[code] / capacity)*100 for code, capacity in settings.COLLEGE_CAPACITIES if fills.get(code, -1) != -1}

    return out

def convert_close_time(end_time):
    delta = end_time - timezone.now()
    return format_timedelta(delta, add_direction=True)

def get_next_phases(user=None):
    phases = []

    for phase in UpdateWindow.objects.get_future_phases():
        phases.append({
            'name': 'College Phase',
            'relative_close_time': convert_close_time(phase.end),
            'phase': phase,
            'eligible': True,
        })

    for phase in RoomPhase.objects.get_future_phases():
        new_phase = {
            'name': phase.name,
            'relative_close_time': convert_close_time(phase.end),
            'phase': phase,
        }

        eligible, errors = phase.is_user_eligible(user)

        new_phase['eligible'] = eligible
        new_phase['errors'] = errors

        phases.append(new_phase)

    return phases