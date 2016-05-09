from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import datetime


# Create your models here.


class Phase(models.Model):
    """
    Base Model for different phases in the allocation process.
    """
    class Meta:
        abstract = True

    name = models.CharField(blank=False)
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
