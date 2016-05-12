from django.conf import settings
from django.db.models import Count
from munkres import Munkres, print_matrix

from roomer.models import UserProfile, UserPreference, Room


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

    out = {code: (fills[code] / capacity) * 100 for code, capacity in settings.COLLEGE_CAPACITIES if
           fills.get(code, -1) != -1}

    return out


def get_cost_matrix(matrix):
    m = Munkres()
    indexes = m.compute(matrix)
    values = []
    for row, column in indexes:
        value = matrix[row][column]
        values.append(value)
    return values


def get_hungarian():
    allocations = []
    users = UserPreference.objects.values("user_id").distinct()
    rooms = Room.objects.filter(assigned_user=None)
    matrix = []
    for idx, user in enumerate(users):
        prefs = UserPreference.objects.filter(user=user["user_id"])
        pref_matrix = []
        for index, room in enumerate(rooms):
            pref_matrix.append(999)
            for pref in prefs:
                if room.id == pref.room_id:
                    pref_matrix[index] = pref.preference_level
        matrix.append(pref_matrix)

    hungarian = get_cost_matrix(matrix)
    for idx, user in enumerate(users):
        allocations.append({"user": user, "preference": hungarian[idx]})
    return allocations


def get_dict_from_key_in_list(k, v, l):
    for d in l:
        if k in d and d[k] == v:
            return d
