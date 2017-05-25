import requests
import json
import datetime

from roomer.ojub_auth import OPENJUB_BASE
from .utils import create_user_dict


def generate_fixture(fixture_file='users.json'):
    r = requests.get(OPENJUB_BASE + "query/active:true%20status:undergrad?limit=1000")

    resp = r.json()

    user_objs = []

    for data in resp['data']:
        # Update or create the user profile
        new_user = {
            'model': 'roomer.userprofile',
            'fields': create_user_dict(data['username'], data)
        }
        user_objs.append(new_user)

    with open(fixture_file, 'w') as f:
        json.dump(user_objs, f)

if __name__ == '__main__':
    generate_fixture()