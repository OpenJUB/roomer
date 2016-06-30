__author__ = 'leonhard'

import csv

import django

from django.core.management.base import BaseCommand
from django.core import management

django.setup()

from roomer.models import UserProfile, Room

class Command(BaseCommand):
    help = 'Exports allocations as CSV files.'

    def handle(self, *args, **options):
        with open('rooms.csv', 'wb') as rooms_file:
            writer = csv.writer(rooms_file)
            writer.writerow(['Room Code', 'Assigned Student Name', 'Assigned Student Username',
                             'College', 'Block', 'Floor'])

            qs = Room.objects.exclude(assigned_user=None)

            for room in qs:
                if room.assigned_user is not None:
                    user_name = room.assigned_user.get_full_name()
                else:
                    user_name = 'Not assigned'

                writer.writerow([room.code, user_name, room.assigned_user.username,
                                room.college, room.block, room.floor])

        with open('users.csv', 'wb') as users_file:
            writer = csv.writer(users_file)
            writer.writerow(['Username', 'Full Name', 'Room Code', 'Email', 'Comment'])

            qs = UserProfile.objects.exclude(allocated_room=None)

            for user in qs:
                if user.allocated_room is not None:
                    user_room_code = user.allocated_room.code
                else:
                    user_room_code = 'None'

                writer.writerow([user.username, user.get_full_name(), user_room_code, user.email, ''])