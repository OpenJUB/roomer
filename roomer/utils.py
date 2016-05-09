
def get_college_code(college_str):
    for college in settings.COLLEGE_CHOICES:
        if college[1] == college_str:
            return college[0]
    return ''
