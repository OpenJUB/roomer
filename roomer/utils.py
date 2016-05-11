import functools
from django.conf import settings

from .models import UserProfile

def get_college_code(college_str):
    for college in settings.COLLEGE_CHOICES:
        if college[1] == college_str:
            return college[0]
    return ''

def get_ordinal(number):
    """
    http://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
    """
    return "{0}{1}".format(number,"tsnrhtdd"[(number/10%10!=1)*(number%10<4)*number%10::4])

def get_points_breakdown(user_profile):
    if user_profile is None:
        return {}

    u = user_profile
    ret = []

    users = [u] + list(u.roommates.all())

    # Add user points
    for user in users:
        ret.append({
            'text': '{0}: {1} year'.format(user.first_name, get_ordinal(user.seniority)),
            'points': user.seniority
        })

        if user.college == user.old_college:
            ret.append({
                'text': ' + college spirit',
                'points': UserProfile.COLLEGE_SPIRIT_POINTS
            })

        if user.extra_points > 0:
            ret.append({
                'text': ' + extra point{2}'
                    .format(user.first_name, user.extra_points, 's' if user.extra_points > 1 else ''),
                'points': user.extra_points
            })

    # Add major, country, region points
    countries = set([val.country for val in users])
    majors = set([val.major for val in users])
    regions = set([val.get_region() for val in users])

    if len(majors) > 1:
        ret.append({
            'text': '{0} majors'.format(len(majors)),
            'points': UserProfile.MAJOR_POINTS * len(majors)
        })

    if len(countries) > 1:
        ret.append({
            'text': '{0} countries'.format(len(countries)),
            'points': UserProfile.COUNTRY_POINTS * len(countries)
        })

    if len(regions) > 1:
        ret.append({
            'text': '{0} regions'.format(len(regions)),
            'points': UserProfile.REGION_POINTS * len(regions)
        })

    sum = 0

    for entry in ret:
        sum += entry['points']

    return {'parts': ret, 'sum': sum}


def tail_call(tuple_return=False):
    """
    Decorator for tail calls. Use with @tail_call
    :param tuple_return:
    :return:
    """
    def __wrapper(func):
        def _optimize_partial(*args, **kwargs):
            old_reference = func.func_globals[func.func_name]
            func.func_globals[func.func_name] = functools.partial(functools.partial, func)

            to_execute = functools.partial(func, *args, **kwargs)

            while isinstance(to_execute, functools.partial):
                to_execute = to_execute()

            func.func_globals[func.func_name] = old_reference
            return to_execute

        def _optimize_tuple(*args, **kwargs):
            while args.__class__ is tuple:
                args = func(*args)

            return args

        if tuple_return:
            functools.update_wrapper(_optimize_tuple, func)
            return _optimize_tuple
        else:
            functools.update_wrapper(_optimize_partial, func)
            return _optimize_partial

    return __wrapper
