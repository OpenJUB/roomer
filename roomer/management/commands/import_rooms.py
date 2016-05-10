__author__ = 'leonhard'

import os

from data_import import import_rooms
from django.core.management.base import BaseCommand
from django.core import management
from roomer import fixtures


class Command(BaseCommand):
    help = 'Imports rooms from old_rooms.json and installs the generated fixture'

    def handle(self, *args, **options):
        in_folder = os.path.dirname(import_rooms.__file__)
        fixture_folder = os.path.dirname(fixtures.__file__)

        in_file = os.path.join(in_folder, 'old_rooms.json')
        out_file = os.path.join(fixture_folder, 'rooms.json')

        print('Generating fixture from {0} to {1}'.format(in_file, out_file))

        # Generate rooms fixture
        import_rooms.generate_fixture(in_file, out_file)


        print('Installing rooms fixture')
        management.call_command('loaddata', 'rooms')