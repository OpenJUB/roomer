#!/usr/bin/env python
__author__ = 'leonhard'

import json
import sys
import os
import django
from django.db.transaction import atomic

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomer.settings")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()

from utils import get_college_code
from roomer.models import UserProfile

with open('old_users.json') as f:
    users = json.load(f)
    username_college = {obj['username']: get_college_code(obj.get('nextCollege', '')) for obj in users if 'username' in obj}

    not_found_count = 0

    with atomic():
        all_users = UserProfile.objects.filter(college='')
        user_count = all_users.count()

        for user in all_users:
            if user.username in username_college:
                user.college = username_college[user.username]
                user.save()
            else:
                not_found_count += 1

    if not_found_count:
        print("{0} of {1} users not found".format(not_found_count, user_count))