from django.contrib.auth import get_user_model

import requests
import datetime

from data_import.utils import create_user_dict

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

        # Update or create the user profile
        user, created = user_model.objects.update_or_create(
            username=uname,
            defaults=create_user_dict(uname, data)
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

                ddict = create_user_dict(stud.username, data)

                for (key, value) in ddict.items():
                    setattr(stud, key, value)

                stud.save()
                print("Updated {}".format(data['username']))
            except ValueError:
                print("Errored {}".format(data['username']))

    def get_allocatable(self, username=None, password=None):
        """ Gets a list of all students that should be allocated """

        r = requests.post(OPENJUB_BASE + "auth/signin",
                          data={'username': username, 'password': password})

        if r.status_code != requests.codes.ok:
            return None

        resp = r.json()

        token = resp['token']

        r2 = requests.get(OPENJUB_BASE +
                          "query/active:true%20status:undergrad",
                          params={'token': token, 'limit': 10000})

        now = datetime.datetime.now()

        def check_year(yr):
            """ Check the year by checking if it is allowed"""

            # if you do not graduate this year, you are allowed to be allocated
            try:
                return int(yr) > (now.year - 2000)
            except:
                return False

        # filter the results by years
        users = filter(lambda u: check_year(u["year"]), r2.json()["data"])

        # and return a list of usernames
        return list(map(lambda u: u["username"], users))

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
