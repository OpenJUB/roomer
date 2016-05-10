
from django.conf import settings

from django.db import models
from django.utils import timezone
from datetime import datetime

# Create your models here.

class UpdateWindowManager(models.Manager):
    def get_future_phases(self):
        now = datetime.now()
        return super(UpdateWindowManager, self).get_queryset().filter(end__gte=now)

class UpdateWindow(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()

    objects = UpdateWindowManager()

    # Allocate first come first serve strategy, but only for unallocated students
    live_allocation = models.BooleanField(default=False)

    def is_open(self):
        now = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
        return self.start <= now < self.end

    def can_update_colleges(self, profile):
        if self.is_open():
            if self.live_allocation:
                return True
            return profile.college == ''
        else:
            return False

    def close(self):
        # TODO Actually allocate people based on preferences
        if self.live_allocation:
            return

    def __str__(self):
        if self.is_open():
            return "Open until " + str(self.end)
        else:
            return "Ended at " + str(self.end)
