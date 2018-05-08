from django.conf import settings
from django.db.models import Count

from roomer.models import UserProfile


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

#returns true if quota hasn't been filled yet
def racial_profiling(country, college):
    country_count = models.UserProfile.objects.filter(college=college).filter(country=country).count()
    return (country_count/get_college_capacity(college)) < settings.MAX_RACE_QUOTA

def can_allocate_to(college_code):
    return not is_full(college_code)


def get_college_fills():
    raw_fills = UserProfile.objects.values('college').annotate(count=Count('college'))

    return {fill['college']: fill['count'] for fill in raw_fills}


def get_fill_percentages():
    fills = get_college_fills()

    out = {code: (float(fills[code]*100) / capacity) for code, capacity in settings.COLLEGE_CAPACITIES if fills.get(code, -1) != -1}

    return out
