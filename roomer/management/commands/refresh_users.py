__author__ = 'twiesing'

import os

from data_import import import_users
from django.core.management.base import BaseCommand
from django.core import management
from roomer import ojub_auth

from getpass import getpass


class Command(BaseCommand):
    help = 'Updates users from OpenJUB'

    def handle(self, *args, **options):
        self.stdout.write("Username: ")
        user = input()
        pwd = getpass("Password for {}:".format(user))

        ojub_auth.OjubBackend().refresh_users(user, pwd)
