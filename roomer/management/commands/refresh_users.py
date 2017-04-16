__author__ = 'twiesing'

import os

from data_import import import_users
from django.core.management.base import BaseCommand
from django.core import management
from roomer import ojub_auth

from getpass import getpass


class Command(BaseCommand):
    help = 'Updates users from OpenJUB'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', nargs='?', default=None,
                            help='Username to use for LDAP. If omitted, ' +
                                 'will ask for username interactively. ')
        parser.add_argument('-p', '--password', nargs='?', default=None,
                            help='Password to use for LDAP. If omitted, ' +
                                 'will ask for password interactively. ')
        parser.add_argument('-s', '--students', nargs='?', default=None,
                            help='JSON file to read students from. See ' +
                                 '\'manage.py export\'')
        parser.add_argument('-c', '--courses', nargs='?', default=None,
                            help='JSON file to read courses from. See ' +
                                 '\'manage.py export\'')

    def get_credentials(self, options):
        if options["username"] is None:
            self.stdout.write("Username: ")
            try:
                input = raw_input
            except NameError:
                pass
            user = input()
        else:
            user = options["username"]

        if options["password"] is None:
            pwd = getpass("Password for %s:" % user)
        else:
            pwd = options["password"]

        return user, pwd

    def handle(self, *args, **options):
        user, pwd = self.get_credentials(options)

        ojub_auth.OjubBackend().refresh_users(user, pwd)
