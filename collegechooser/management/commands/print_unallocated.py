__author__ = 'twiesing'

from django.core.management.base import BaseCommand
from django.db.models import Q

from roomer import ojub_auth
from getpass import getpass

from roomer.models import UserProfile

class Command(BaseCommand):
    help = 'Dumps a list of all active undergraduates that have not been ' \
           'allocated to a college yet'

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

        # fetch all allocatable users
        user, pwd = self.get_credentials(options)
        allocatable = ojub_auth.OjubBackend().get_allocatable(user, pwd)

        # fetch all the students that have been allocated to a college
        nametuples = UserProfile.objects.filter(~Q(college = '')).values_list(
            'username')
        names = list(map(lambda nt:nt[0], nametuples))

        # find the ones who have not yet been allocated
        notyet = list(filter(lambda un: un not in names, allocatable))

        for name in notyet:
            print(name)

        print("----------------------------------------------")
        print("Summary: {} user(s) still need to be allocated".format(len(
            notyet)))