
from django.db import models
from django.utils import timezone

# Create your models here.


class UpdateWindow(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()

    # Allocate first come first serve strategy
    live_allocation = models.BooleanField(default=False)

    # Only allow unallocated students to change records
    only_unallocated = models.BooleanField(default=False)

    def is_open(self):
        now = timezone.now()
        return self.start <= now < self.end

    def can_update_colleges(self, profile):
        if not self.is_open():
            return False
        else:
            if self.only_unallocated and profile.college:
                return False
            else:
                return True

    def close(self):
        # TODO Actually allocate people based on preferences
        pass

    def __str__(self):
        if self.is_open():
            return "Open until " + str(self.end)
        else:
            return "Ended at " + str(self.end)
