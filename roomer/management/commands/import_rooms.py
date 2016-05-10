__author__ = 'leonhard'

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Imports rooms from old_rooms.json'