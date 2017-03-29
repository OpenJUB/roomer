from django.contrib.auth import get_user_model
from roomer.utils import get_college_code

import requests
import datetime

OPENJUB_BASE = "https://legacyapi.jacobs.university/"


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

        try:
            year = int(data['year'])
        except ValueError:
            year = now.year

        # Update or create the user profile
        user, created = user_model.objects.update_or_create(
            username=uname,
            defaults={
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
        )

        if created:
            user.set_unusable_password()
            if user.username in ["lkuboschek", "sshukla"]:
                user.is_staff = True
                user.is_superuser = True

        user.save()

        return user


    def refresh_users(self, username=None, password=None):
        r = requests.post(OPENJUB_BASE + "auth/signin",
                          data={'username': username, 'password': password})

        if r.status_code != requests.codes.ok:
            return None

        resp = r.json()

        token = resp['token']

        now = datetime.datetime.now()


        user_model = get_user_model()
        for stud in user_model.objects.all():
            r2 = requests.get(OPENJUB_BASE + "user/name/{}"
                               .format(stud.username),
                               params={'token': token})

            if r2.status_code != requests.codes.ok:
                print(r2.json())
                print("Skipped {}".format(stud.username))
                continue

            data = r2.json()
            try:

                try:
                    year = int(data['year'])
                except ValueError:
                    year = now.year

                ddict = {
                    'username': stud.username,
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



                for (key, value) in ddict.items():
                    setattr(stud, key, value)

                stud.save()
                print("Updated {}".format(data['username']))
            except ValueError:
                print("Errored {}".format(data['username']))


    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None