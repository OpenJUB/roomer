COLLEGE_CHOICES = [
    ('NM', 'Nordmetall'),
    ('C3', 'C3'),
    ('KR', 'Krupp'),
    ('ME', 'Mercator')
]


def get_college_code(college_str):
    for college in COLLEGE_CHOICES:
        if college[1] == college_str:
            return college[0]
    return ''


def create_user_dict(uname, data):
    """ Creates a dictionary representing a user from a json object """

    import datetime
    now = datetime.datetime.now()

    try:
        year = int(data['year'])
    except ValueError:
        year = now.year

    return {
        'username': uname,
        'first_name': data['firstName'],
        'last_name': data['lastName'],
        'email': data['email'],
        'status': data['status'],
        'seniority': now.year - 2000 - year + 3,
        'year': int(data['year']),
        'major': data['major'],
        'country': data['country'],
        'old_college': get_college_code(data['college']),
    }
