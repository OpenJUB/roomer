import json
import sys

from django.contrib.auth import get_user_model

from data_import import utils
from data_import.utils import create_user_dict
from roomer.models import Room, UserProfile

__author__ = 'twiesing'

import os

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Finds all users that are in need of a room, but are not in the system'

    def handle(self, *args, **options):
        with open("students.json") as fn:
            students = json.load(fn)

        # create a set of virtual users from students.json
        UserModel = get_user_model()
        virtual_users = [UserModel(**create_user_dict(s["username"], s)) for s in students if s["active"]]

        # create a list of users from the real system
        real_users = [u[0] for u in  UserProfile.objects.all().values_list("username")]

        c = 0
        for vu in virtual_users:
            if vu.needs_room and not vu.username in real_users:
                print(vu.first_name, vu.last_name)
                c+= 1
        print(c)

