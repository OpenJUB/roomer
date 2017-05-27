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

    out = {code: (float(fills[code]) / capacity) * 100 for code, capacity in settings.COLLEGE_CAPACITIES if
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
        allocate_one(allocation)

def allocate_one(allocation):
    try:
        user = UserProfile.objects.get(id=allocation["user"]["user_id"])

        if allocation['preference'] < 999:
            user_pref = UserPreference.objects.filter(user=user, preference_level=allocation["preference"]).first()
            print("User " + user.username + " to room " + user_pref.room.code)

            user.allocated_room = user_pref.room
            user.save()

            # Also allocate roommates
            mate_associations = zip(user.roommates.all(), user_pref.room.associated.all())

            for mate, room in mate_associations:
                mate.allocated_room = room
                mate.save()

                # Clear their preferences
                UserPreference.objects.filter(user=mate).delete()

            # Clear their preferences
            UserPreference.objects.filter(user=user).delete()
    except Exception as e:
        raise e
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

        run_better_thing(user_prefs)

def get_allocations_for_unallocated_users_old(point_limit):
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

x = get_allocations_for_unallocated_users_old
y = get_allocations_for_unallocated_users


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

def run_better_thing(users):
    """
        :param users: Set of users with a given user level
    """

    user_objects = list(map(
        lambda u:u["user_id"],
        users
    ))

    # find all preferences that are needed
    prefs = lambda:UserPreference.objects.filter(
        user__in = user_objects
    ).order_by('preference_level')

    # go over all the rooms that are involved
    rooms = prefs().values('room').distinct()

    for r in rooms:
        room = Room.objects.get(id=r["room"])

        try:
            room.assigned_user
            has_user = True
        except:
            has_user = False

        is_disabled = room.has_tag('disabled')

        for proom in room.associated.all():
            if proom.has_tag('disabled'):
                is_disabled = True
                break

        if not is_disabled and not has_user:

            try:
                # find the highest prefernce
                level = prefs().filter(room = room).first().preference_level
            except AttributeError:
                continue

            # all the ones for the current level
            choices = prefs().filter(room = room, preference_level = level).order_by('?')

            # take the first one
            choice = choices.first()

            # store in the list of allocations
            allocate_one({
                "user": {"user_id": choice.user.id},
                "preference": choice.preference_level
            })


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
