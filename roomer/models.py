from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, ValidationError
from utils import get_college_code
from .regions import regions


class CollegeField(models.CharField):
    def __init__(self, *args, **kwargs):

        # Remove args that we set ourselves
        if 'max_length' in kwargs:
            del kwargs['max_length']

        if 'choices' in kwargs:
            del kwargs['choices']

        super(CollegeField, self).__init__(*args, max_length=2, choices=settings.COLLEGE_CHOICES, **kwargs)


class UserProfile(AbstractUser):
    REQUEST_INVALID = 0
    REQUEST_SENT = 1
    REQUEST_MUTUAL = 2

    COLLEGE_SPIRIT_POINTS = 0.5
    COUNTRY_POINTS = 1
    REGION_POINTS = 0.5
    MAJOR_POINTS = 0.5

    year = models.IntegerField(editable=False)
    major = models.CharField(max_length=128, editable=False)
    country = models.CharField(max_length=64, editable=False)

    # TODO Write a custom validator. format like: "C3:NM:KR:ME"
    college_pref = models.CharField(max_length=11, blank=True)

    # How many years this person has been at university
    seniority = models.IntegerField(editable=False)

    # Extra points, added manually by the admin
    extra_points = models.IntegerField(default=0)

    old_college = CollegeField(editable=False)
    college = CollegeField(blank=True)

    points = models.DecimalField(default=0, decimal_places=3, max_digits=6, blank=True, editable=False)
    roommates = models.ManyToManyField("self", blank=True)

    def send_roommate_request(self, other):
        """ Creates a request, also checking if another request in the opposite direction
            already exists.

            :arg other Another UserProfile instance
            :returns Truthy if request sent, Falsy if request not valid. Return codes declared in this class
        """

        # You can't room with yourself
        if self == other:
            return self.REQUEST_INVALID

        if self.college != other.college:
            return self.REQUEST_INVALID

        req, _ = RoommateRequest.objects.get_or_create(sender=self, receiver=other)

        if not req.check_mutual():
            req.save()
            return self.REQUEST_SENT
        else:
            return self.REQUEST_MUTUAL

    def remove_roommate(self, other):
        if other not in self.roommates.all():
            return False
        else:
            self.roommates.remove(other)

            # Also remove it from our roommates' lists
            for mate in self.roommates.all():
                mate.roommates.remove(other)
                mate.save()

    def get_region(self):
        for key, value in regions.items():
            if self.country in value:
                return key

        return "other"

    def update_points(self, ignore_roommates=False):
        """
            Updates the points for this user, and all of his roommates
            :arg ignore_roommates Don't update this users' roommates. Defaults to False
        """
        if not self.points:
            return

        # Start with seniority
        self.points = self.seniority
        self.points += self.extra_points

        # Add college spirit
        if self.college == self.old_college:
            self.points += self.COLLEGE_SPIRIT_POINTS

        # Only check the m2m manager if we're saved already
        if self.pk:
            for mate in self.roommates.all():
                # Update the roommates' points as well
                if not ignore_roommates:
                    mate.update_points()

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
        super(UserProfile, self).save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        if self.get_full_name():
            return self.get_full_name()
        else:
            return self.get_username()


class Room(models.Model):
    ROOM_CODE_REGEX = r'[A-Z]{2}-\d{3}'

    SINGLE_ROOM_TAG = 'single'
    DOUBLE_ROOM_TAG = 'double'
    TRIPLE_ROOM_TAG = 'triple'
    TALL_ROOM_TAG = 'tall'
    QUIET_ROOM_TAG = 'quiet'
    DISABLED_ROOM_TAG = 'disabled'

    # TODO Write format validator
    code = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=ROOM_CODE_REGEX,
                message='Enter a valid room code.'
            )]
    )

    college = models.ForeignKey('College')

    floor = models.IntegerField()
    block = models.CharField(max_length=1)

    # Associated rooms belong together, think apartments
    associated = models.ManyToManyField("self", blank=True)

    def add_tag(self, tag, generated=False, raise_exception=False):
        try:
            self.tags.create(room=self, generated=generated, tag=tag)
        except ValidationError as e:
            if raise_exception:
                raise e

    def update_generated_tags(self):
        self.tags.filter(generated=True).delete()

        new_tags = []

        no_associated = self.associated.count()

        if no_associated == 1:
            new_tags.append(RoomTag(room=self, generated=True, tag=self.DOUBLE_ROOM_TAG))
        elif no_associated == 2:
            new_tags.append(RoomTag(room=self, generated=True, tag=self.TRIPLE_ROOM_TAG))
        elif no_associated == 0:
            new_tags.append(RoomTag(room=self, generated=True, tag=self.SINGLE_ROOM_TAG))

        self.tags.bulk_create(new_tags)

    def save(self, **kwargs):
        # Save ourselves if we're not in the DB, so we can use m2m field
        if not self.pk:
            super(Room, self).save(kwargs)

        # Update boolean fields
        for room in self.associated.all():
            room.update_generated_tags()
            room.save()

        self.update_generated_tags()

        super(Room, self).save(kwargs)

    def __str__(self):
        return self.code


class RoomTag(models.Model):
    VALID_TAG_LIST = [
        ('quiet', 'quiet'),
        ('tall', 'tall'),
        ('disabled', 'disabled'),
        ('single', 'single'),
        ('double', 'double'),
        ('triple', 'triple'),
    ]

    room = models.ForeignKey(Room, related_name='tags')
    tag = models.CharField(max_length=30, choices=VALID_TAG_LIST)

    generated = models.BooleanField(default=False)

    class Meta:
        unique_together = ('room', 'tag')

    def __str__(self):
        return self.room.code + " [" + self.tag + "]"


class College(models.Model):
    name = CollegeField()

    def __str__(self):
        return self.get_name_display()


# TODO Check if people are already roommates when creating request
class RoommateRequest(models.Model):
    sender = models.ForeignKey(UserProfile, related_name='outbox')
    receiver = models.ForeignKey(UserProfile, related_name='inbox')

    class Meta:
        unique_together = ('sender', 'receiver')

    def accept(self):
        # Add ourselves to their roommates
        self.receiver.roommates.add(self.sender)

        # Add our roommates to their roommates
        for mate in self.sender.roommates.all():
            if mate != self.receiver:
                self.receiver.roommates.add(mate)

        self.receiver.save()

        # Also add the new roommate to our other roommates
        for mate in self.receiver.roommates.all():
            if mate != self.sender:
                mate.roommates.add(self.sender)
                mate.save()

        self.delete()

    def check_mutual(self):

        # If the recipient is already a roommate of the sender, delete the request
        if self.receiver in self.sender.roommates.all():
            self.delete()

        try:
            reverse = RoommateRequest.objects.get(sender=self.receiver, receiver=self.sender)

            # If we get here, someone else has already sent a request the other way. We can make them roommates,
            # and delete these requests

            # Only this is required, since the relation is symmetrical
            reverse.accept()
            self.delete()

            return True
        except RoommateRequest.DoesNotExist:
            return False

    def __str__(self):
        return str(self.sender) + " to " + str(self.receiver)
