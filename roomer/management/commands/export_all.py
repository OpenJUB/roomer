import sys

from roomer.models import Room, UserProfile

__author__ = 'twiesing'

import os

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Exports all data from the system so that it can be passed to housing'

    def handle(self, *args, **options):

        # iterate over all the rooms and show if the rooms are allocated
        for (p, n) in settings.COLLEGE_CHOICES:
            print("# COLLEGE {}".format(n))
            for r in Room.objects.filter(college=p).order_by('code'):
                sys.stdout.write(r.code + ', ')
                try:
                    if r.assigned_user.housing_type == settings.HOUSING_TYPE_FRESHIE:
                        sys.stdout.write('(freshmen roommate wanted) \n')
                    else:
                        sys.stdout.write(r.assigned_user.get_full_name() + '\n')
                except:
                    sys.stdout.write('\n')

        print()

        # Users without Room
        for (p, n) in settings.COLLEGE_CHOICES:
            print("# Users without room in {}".format(n))
            for u in UserProfile.objects.filter(college=p, allocated_room=None):
                if u.housing_type != settings.HOUSING_TYPE_FRESHIE:
                    row = [
                              u.get_full_name()
                          ] + list(
                        map(lambda uu: u.get_full_name(), u.roommates.all())
                    )

                    if len(row) == 1:
                        row += ['']

                    print(','.join(row))

        print()
        # Users without college
        print("# Users without college")
        for u in UserProfile.objects.all():
            if u.allocated_room is None and u.college is None and u.housing_type != settings.HOUSING_TYPE_FRESHIE:
                row = [
                    u.get_full_name()
                ] + list(
                    map(lambda uu: u.get_full_name(), u.roommates.all())
                )

                if len(row) == 1:
                    row += ['']

                print(','.join(row))
