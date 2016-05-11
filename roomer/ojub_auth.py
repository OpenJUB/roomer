from django.contrib.auth import get_user_model

from roomer.utils import get_college_code

import requests
import datetime

OPENJUB_BASE = "https://api.jacobs-cs.club/"


class OjubBackend(object):
    """
    Authenticates credentials against the OpenJUB database.

    The URL for the server is configured by OPENJUB_BASE in the settings.

    This class does not fill in user profiles, this has to be handled
    in other places
    """
    def authenticate(self, username=None, password=None):
        r = requests.post(OPENJUB_BASE + "auth/signin",
                          data={'username': username, 'password': password})

        if r.status_code != requests.codes.ok:
            return None

        resp = r.json()

        uname = resp['user']
        token = resp['token']

        details = requests.get(OPENJUB_BASE + "user/me",
                               params={'token': token})

        if details.status_code != requests.codes.ok:
            return None

        data = details.json()

        user_model = get_user_model()
        now = datetime.datetime.now()

        # Update or create the user profile
        user, created = user_model.objects.update_or_create(
            username=uname,
            defaults={
                'username': uname,
                'first_name': data['firstName'],
                'last_name': data['lastName'],
                'email': data['email'],
                'seniority': now.year - 2000 - int(data['year']) + 3,
                'year': int(data['year']),
                'major': data['major'],
                'country': data['country'],
                'old_college': get_college_code(data['college']),
            }
        )

        if created:
            user.set_unusable_password()
            if user.username in ["lkuboschek", "sshukla"]:
                user.is_staff = True
                user.is_superuser = True

        user.save()

        return user


    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None