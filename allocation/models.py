from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import datetime


# Create your models here.
from roomer.models import UserProfile, Room


class Phase(models.Model):
    """
    Base Model for different phases in the allocation process.
    """
    class Meta:
        abstract = True

    name = models.CharField(max_length=64, blank=False)
    start = models.DateTimeField()
    end = models.DateTimeField()
    live_allocation = models.BooleanField(default=False)

    def is_open(self):
        now = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
        return self.start <= now < self.end

    def can_update(self, profile):
        if self.is_open() and self.live_allocation:
            return True
        else:
            return False

    def __str__(self):
        if self.is_open():
            return "Open until " + str(self.end)
        else:
            now = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
            if now < self.start:
                return "Starts on " + str(self.start) + " and Ends on " + str(self.end)
            else:
                return "Ended on " + str(self.end)


class RoomPhase(Phase):
    """
    Model for Room Phases (Quite Block Allocation, Tall Room
    Allocation, Triple Apartment Allocation, and Point based Allocations.)
    """
    is_tall_phase = models.BooleanField(default=False)
    is_single_phase = models.BooleanField(default=False)  # For Psychos
    is_triple_phase = models.BooleanField(default=False)  # Apparently triple rooms need their own phase
    points_limit = models.FloatField(default=0, blank=True)  # Setting points. Default 0 to allow everybody

    def can_update(self, profile):
        if self.is_open():
            if self.tag in profile.tags:
                return True
            else:
                return False

    def is_user_eligible(self, user: UserProfile):
        error = []

        # Check for right year of study
        now = datetime.now()

        # TODO Allow whitelisted users

        # Check user generally eligible
        if user.year >= now.year:
            error.append('You are a third year student and therefore not eligible for this round.')

        # Check user eligible by points
        if user.points < self.points_limit:
            error.append('You do not have enough points to choose a room in this round. '
                         'You have {0} of {1} required points.'.format(user.points, self.points_limit))

        # Check user eligible for tall room phase
        if self.is_tall_phase and not user.is_tall:
            error.append('A tall room phase is currently active. However, you are not tall.'
                         'If you believe that you are tall, send your username to housing@ju-u.sg')

        if self.is_single_phase:
            required_count = 0
        elif self.is_triple_phase:
            required_count = 2
        else:
            required_count = 1

        if user.roommates.count() != required_count:
            error.append('You have {0} roommate(s), but the current phase requires {1} roommate(s).'.format(
                user.roommates.count(),
                required_count
            ))

        return not len(error) > 0, error

    def is_allocating_room(self, room: Room):
        if self.is_tall_phase:
            if not room.has_tag(room.TALL_ROOM_TAG):
                return False, 'Not a tall room.'

        if self.is_triple_phase:
            if not room.has_tag(room.TRIPLE_ROOM_TAG):
                return False, 'Not a triple room.'

        if self.is_single_phase:
            if not room.has_tag(room.SINGLE_ROOM_TAG):
                return False, 'Not a single room.'

        if not room.has_tag(room.DOUBLE_ROOM_TAG):
            return False, 'Not a double room.'

        return True, 'All good!'



class CollegePhase(Phase):
    """
    Model for College selection phase
    """
    def can_update(self, profile):
        if self.is_open():
            if self.live_allocation:
                return True
            return profile.college == ''
        else:
            return False
