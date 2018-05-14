__author__ = 'twiesing'

from django.core.management.base import BaseCommand
from django.core import management

import random
from collegechooser import utils

from roomer.models import UserProfile

class Command(BaseCommand):
    help = 'Imports rooms from old_rooms.json and installs the generated fixture.'

    def molest(self, user):
        """ Allocates a user to a college of their choice """

        for c in user.college_pref.split(':'):
            if utils.can_allocate_to(c) and utils.racial_profiling(user.country, c):
                user.college = c
                user.save()
                print("Allocated {} to {}".format(user.username, c))
                return True

        print("All colleges are full, can not allocate {}".format(
            user.username))
        return False

    def handle(self, *args, **options):
        pot = UserProfile.objects.filter(college='').exclude(
            college_pref='')

        pot = list(sorted(pot, key=lambda u:u.seniority_points))

        while len(pot) != 0:

            # while we have some students we get all of the ones in the
            # current seniority

            seniors = pot[0].seniority_points

            studs = list(filter(lambda u:u.seniority_points == seniors, pot))
            pot = list(filter(lambda u:u.seniority_points != seniors, pot))

            # and iterate through them randomly
            random.shuffle(studs)
            for stud in studs:
                self.molest(stud)
