import StringIO
import codecs

__author__ = 'leonhard'

import csv

import django

from django.core.management.base import BaseCommand
from django.core import management

django.setup()

from roomer.models import UserProfile, Room


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class Command(BaseCommand):
    help = 'Exports allocations as CSV files.'

    def handle(self, *args, **options):
        with open('rooms.csv', 'wb') as rooms_file:
            writer = UnicodeWriter(rooms_file)
            writer.writerow(['Room Code', 'Assigned Student Name', 'Assigned Student Username',
                             'College', 'Block', 'Floor'])

            qs = Room.objects.exclude(assigned_user=None)

            for room in qs:
                if room.assigned_user is not None:
                    user_name = room.assigned_user.get_full_name()
                else:
                    user_name = 'Not assigned'

                writer.writerow([room.code, user_name, room.assigned_user.username,
                                room.college, room.block, str(room.floor)])

        with open('users.csv', 'wb') as users_file:
            writer = UnicodeWriter(users_file)
            writer.writerow(['Username', 'Full Name', 'Room Code', 'Email', 'Comment'])

            qs = UserProfile.objects.exclude(allocated_room=None)

            for user in qs:
                if user.allocated_room is not None:
                    user_room_code = user.allocated_room.code
                else:
                    user_room_code = 'None'

                writer.writerow([user.username, user.get_full_name(), user_room_code, user.email, ''])