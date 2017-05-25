from django.conf import settings


def get_college_code(college_str):
    for college in settings.COLLEGE_CHOICES:
        if college[1] == college_str:
            return college[0]
    return ''


def get_housing_code(type_string):
    for tp in settings.HOUSING_TYPES:
        if tp[1] == type_string:
            return tp[0]

    return get_housing_code(settings.HOUSING_TYPE_UNKNOWN)


def get_housing_string(type_code):
    for tp in settings.HOUSING_TYPES:
        if tp[0] == type_code:
            return tp[1]

    return settings.HOUSING_TYPE_UNKNOWN


def get_housing_type(data):
    """ Gets the housing type a student has"""

    # get the current year
    import datetime
    now = datetime.datetime.now()

    # load the year of the student
    try:
        year = int(data['year'])
    except ValueError:
        year = now.year

    # Compute the year of study
    study_year = now.year - 2000 - year + 3

    # get the status
    status = data['status']

    if status == 'foundation-year':
        return get_housing_code(settings.HOUSING_TYPE_FOUNDATION_YEAR)
    elif status == 'undergrad':
        if study_year == 1:
            return get_housing_code(settings.HOUSING_TYPE_UG_1)
        elif study_year == 2:
            return get_housing_code(settings.HOUSING_TYPE_UG_2)
        else:
            return get_housing_code(settings.HOUSING_TYPE_UG_3)
    elif status == 'master':
        if study_year == 1:
            return get_housing_code(settings.HOUSING_TYPE_MS_1)
        else:
            return get_housing_code(settings.HOUSING_TYPE_MS_2)

    return get_housing_code(settings.HOUSING_TYPE_UNKNOWN)


def create_user_dict(uname, data):
    """ Creates a dictionary representing a user from a json object """

    return {
        'username': uname,
        'first_name': data['firstName'],
        'last_name': data['lastName'],
        'email': data['email'],
        'status': data['status'],
        'housing_type': get_housing_type(data),
        'year': int(data['year']),
        'major': data['major'],
        'country': data['country'],
        'old_college': get_college_code(data['college']),
    }
