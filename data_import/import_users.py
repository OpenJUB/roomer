import requests
import json
import datetime

from utils import get_college_code


def generate_fixture(fixture_file='users.json'):
    openjub_base = "https://api.jacobs-cs.club/"

    r = requests.get(openjub_base + "query/active:true%20status:undergrad?limit=1000")

    resp = r.json()

    user_objs = []

    now = datetime.datetime.now()

    for data in resp['data']:
        # Update or create the user profile
        new_user = {
            'model': 'roomer.userprofile',
            'fields': {
                'username': data['username'],
                'first_name': data['firstName'],
                'last_name': data['lastName'],
                'email': data['email'],
                'seniority': now.year - 2000 - int(data['year']) + 3 if data['year'] != '' else 0,
                'year': int(data['year']) if data['year'] != '' else 0,
                'major': data['major'],
                'country': data['country'],
                'old_college': get_college_code(data['college']),
            }
        }
        user_objs.append(new_user)

    with open(fixture_file, 'w') as f:
        json.dump(user_objs, f)

if __name__ == '__main__':
    generate_fixture()