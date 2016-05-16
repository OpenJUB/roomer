from django.conf import settings
from django.db.models import Count
from munkres import Munkres, print_matrix

from roomer.models import UserProfile, UserPreference, Room


def frange(a,b,s):
    return [] if s > 0 and a > b or s < 0 and a < b or s==0 else [a]+frange(a+s,b,s)


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


def allocate(allocations):
    for allocation in allocations:
        try:
            user = UserProfile.objects.get(id=allocation["user"]["user_id"])

            if allocation['preference'] < 999:
                user_pref = UserPreference.objects.get(user=user, preference_level=allocation["preference"])
                print("User " + user.username + " to room " + user_pref.room.code)

                user.allocated_room = user_pref.room
                user.save()


                # Also allocate roommates
                mate_associations = zip(user.roommates.all(), user_pref.room.associated.all())

                for user, room in mate_associations:
                    user.allocated_room = room
                    user.save()

                user_pref.delete()

        except:
            raise Exception("Allocation fucked up! Blame Eurovision #AustraliaFor2017")


def get_allocations_for_unallocated_users(point_limit):
    for pt in frange(15, point_limit, -0.5):
        users = UserProfile.objects.filter(allocated_room=None, points__gte=pt)

        user_ids = []
        user_prefs = []
        for user in users:
            if user.id not in user_ids:
                user_prefs.append({"user_id": user.id})
                user_ids.append(user.id)

        if users.count() > 0:
            print("Allocating {0} users with {1} or more points".format(users.count(), pt))

        try:
            allocations = run_hungarian(user_prefs)
        except:
            raise Exception("Hungarian failure")
        try:
            allocate(allocations)
        except:
            raise Exception("Allocation failure")

x = get_allocations_for_unallocated_users


def run_hungarian(users):
    allocations = []

    # Shortcut for the hungarian
    if len(users) == 0:
        return []

    unassigned_rooms = Room.objects.filter(assigned_user=None)
    rooms = []
    for room in unassigned_rooms:
        if not room.has_tag('disabled'):
            rooms.append(room)

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


def disable_floor(college, floor):
    college_list = settings.COLLEGE_CODES
    if college not in college_list:
        raise Exception("Unidentified College")
    rooms_to_disable = Room.objects.filter(college=college, floor=floor)
    for room in rooms_to_disable:
        room.add_tag('disabled')



