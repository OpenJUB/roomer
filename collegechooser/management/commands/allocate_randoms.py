__author__ = 'twiesing'

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core import management

import random
from collegechooser import utils

from roomer.models import UserProfile
from .allocate_colleges import Command as NAC

class Command(NAC):
    help = 'Allocate users without college preference into a random college. '

    def molest(self, user):
        """ Allocates a user to a college of their choice """

        colleges = [c[0] for c in settings.COLLEGE_CHOICES]
        random.shuffle(colleges)

        for c in colleges:
            if self.try_allocate(self, user, c):
                return True

        print("All colleges are full, can not allocate {}".format(
            user.username))
        return False

    def handle(self, *args, **options):
        pot = UserProfile.objects.filter(college='').filter(college_pref='')

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
