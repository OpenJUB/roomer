__author__ = 'leonhard'

import os

from data_import import import_users
from django.core.management.base import BaseCommand
from django.core import management
from roomer import fixtures


class Command(BaseCommand):
    help = 'Imports rooms from old_rooms.json and installs the generated fixture'

    def handle(self, *args, **options):
        fixture_folder = os.path.dirname(fixtures.__file__)

        out_file = os.path.join(fixture_folder, 'users.json')

        print('Generating fixture to {0}'.format(out_file))

        # Generate rooms fixture
        import_users.generate_fixture(out_file)


        print('Installing users fixture')
        management.call_command('loaddata', 'users')