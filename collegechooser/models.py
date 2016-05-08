
from django.conf import settings

from django.db import models
from django.utils import timezone

# Create your models here.


class UpdateWindow(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()

    # Allocate first come first serve strategy, but only for unallocated students
    live_allocation = models.BooleanField(default=False)

    def is_open(self):
        now = timezone.make_aware(timezone.now(), timezone.get_current_timezone())
        return self.start <= now < self.end

    def can_update_colleges(self, profile):
        if self.is_open():
            if self.live_allocation:
                return profile.college == ''
            return True
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
