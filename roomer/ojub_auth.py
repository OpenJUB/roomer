from django.conf import settings
from django.contrib.auth.models import User

from roomer.models import UserProfile

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
                          data = {'username':username, 'password': password})

        if r.status_code != requests.codes.ok:
            return None

        resp = r.json()

        uname = resp['user']
        token = resp['token']

        details = requests.get(OPENJUB_BASE + "user/me",
                       params = {'token':token})

        if details.status_code != requests.codes.ok:
            return None

        try:
            user = User.objects.get(username=uname)
        except User.DoesNotExist:
            user = User(username=uname)

            user.set_unusable_password()

            # TODO Don't hardcode this
            if user.username in ["lkuboschek", "sshukla"]:
                user.is_staff = True
                user.is_superuser = True

            data = details.json()

            user.first_name = data['firstName']
            user.last_name = data['lastName']
            user.email = data['email']

            user.save()

        now = datetime.datetime.now()

        details_obj = details.json()

        # Update part of the user profile
        profile, created = UserProfile.objects.update_or_create(
            user=user,
            year=int(details_obj['year']),
            major=details_obj['majorShort'],
            country=details_obj['country'],
            old_college=details_obj['college'],
            defaults={
                'seniority': now.year - 2000 - int(details_obj['year']) + 3,
            }
        )

        profile.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None