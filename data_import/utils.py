COLLEGE_CHOICES = [
    ('NM', 'Nordmetall'),
    ('C3', 'C3'),
    ('KR', 'Krupp'),
    ('ME', 'Mercator'),
    ('CV', 'College V')
]


def get_college_code(college_str):
    for college in COLLEGE_CHOICES:
        if college[1] == college_str:
            return college[0]
    return ''