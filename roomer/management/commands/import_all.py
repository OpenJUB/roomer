__author__ = 'leonhard'

from django.core.management.base import BaseCommand
from django.core import management

class Command(BaseCommand):
    help = 'Imports rooms from old_rooms.json and installs the generated fixture.'

    def handle(self, *args, **options):
        management.call_command('import_rooms')
        management.call_command('import_users')