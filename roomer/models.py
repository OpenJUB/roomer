from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import CharField

from .regions import regions

# Create your models here.
COLLEGE_CHOICES = [
    ('NM', 'Nordmetall'),
    ('C3', 'C3'),
    ('KR', 'Krupp'),
    ('ME', 'Mercator')
]


class CollegeField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(CollegeField, self).__init__(*args, max_length=2, choices=COLLEGE_CHOICES)


class UserProfile(models.Model):
    REQUEST_SENT = 1
    REQUEST_MUTUAL = 2

    COLLEGE_SPIRIT_POINTS = 0.5
    COUNTRY_POINTS = 1
    REGION_POINTS = 0.5
    MAJOR_POINTS = 0.5

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    year = models.IntegerField()
    major = models.CharField(max_length=128)
    country = models.CharField(max_length=64)

    # TODO Write a custom validator. format like: "C3:NM:KR:ME"
    college_pref = models.CharField(max_length=11, blank=True)

    # TODO Initialize this field properly
    # How many years this person has been at university
    seniority = models.IntegerField()

    old_college = CollegeField()
    college = CollegeField()

    points = models.DecimalField(decimal_places=3, max_digits=6, blank=True)
    roommates = models.ManyToManyField("self", blank=True)

    def send_roommate_request(self, other):
        req, _ = RoommateRequest.objects.get_or_create(sender=self, receiver=other)

        if not req.check_mutual():
            req.save()
            return self.REQUEST_SENT
        else:
            return self.REQUEST_MUTUAL

    def get_region(self):
        for key, value in regions.items():
            if self.country in value:
                return key

        return "other"

    def update_points(self):
        # Start with seniority
        self.points = self.seniority

        # Add college spirit
        if self.college == self.old_college:
            self.points += self.COLLEGE_SPIRIT_POINTS

        # Only check the m2m manager if we're saved already
        if self.pk:
            for mate in self.roommates.all():
                # Nationality points
                if self.country != mate.country:
                    self.points += self.COUNTRY_POINTS

                # Region points
                if self.get_region() != mate.get_region():
                    self.points += self.REGION_POINTS

                # Major points
                if self.major != mate.major:
                    self.points += self.MAJOR_POINTS

    def save(self, *args, **kwargs):
        self.update_points()
        super(UserProfile, self).save(*args, **kwargs) # Call the "real" save() method.


    def __str__(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.user.get_username()


class Room(models.Model):
    # TODO Write format validator
    code = models.CharField(max_length=8)
    floor = models.IntegerField()
    block = models.CharField(max_length=1)

    # TODO Implement room flags (tall, quiet, etc.)

    # Associated rooms belong together, think apartments
    associated = models.ManyToManyField("self")


class College(models.Model):
    name = CollegeField()
    rooms = models.ManyToManyField(Room)


# TODO Check if people are already roommates when creating request
class RoommateRequest(models.Model):
    sender = models.ForeignKey(UserProfile, related_name='outbox')
    receiver = models.ForeignKey(UserProfile, related_name='inbox')

    class Meta:
        unique_together = ('sender', 'receiver')

    def accept(self):
        self.sender.roommates.add(self.receiver)
        self.sender.save()
        self.delete()

    def check_mutual(self):
        try:
            reverse = RoommateRequest.objects.get(sender=self.receiver, receiver=self.sender)

            # If we get here, someone else has already sent a request the other way. We can make them roommates,
            # and delete these requests

            # Only this is required, since the relation is symmetrical
            self.sender.roommates.add(self.receiver)
            self.sender.save()

            reverse.delete()
            self.delete()

            return True
        except RoommateRequest.DoesNotExist:
            return False

    def __str__(self):
        return str(self.sender) + " to " + str(self.receiver)
