from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, ValidationError
from .utils import get_college_code
from .regions import regions

from decimal import Decimal

class CollegeField(models.CharField):
    def __init__(self, *args, **kwargs):

        # Remove args that we set ourselves
        if 'max_length' in kwargs:
            del kwargs['max_length']

        if 'choices' in kwargs:
            del kwargs['choices']

        super(CollegeField, self).__init__(*args, max_length=2, choices=settings.COLLEGE_CHOICES, **kwargs)


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class UserPreference(models.Model):
    preference_level = IntegerRangeField(min_value=1, max_value=7)
    user = models.ForeignKey("UserProfile")
    room = models.ForeignKey("Room")


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
    allocated_room = models.OneToOneField("Room", related_name='assigned_user', blank=True, null=True)
    allocation_preferences = models.ManyToManyField("Room", through="UserPreference", blank=True)

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

    def get_user_points(self):
        points = self.seniority + self.extra_points

        if self.old_college == self.college:
            points += self.COLLEGE_SPIRIT_POINTS

        return points

    def update_points(self, ignore_roommates=False):
        """
            Updates the points for this user, and all of his roommates
            :arg ignore_roommates Don't update this users' roommates. Defaults to False
        """

        roommates = list(self.roommates.all())
        roommates.append(self)

        countries = set([val.country for val in roommates])
        majors = set([val.major for val in roommates])
        regions = set([val.get_region() for val in roommates])
        user_points = [val.get_user_points() for val in roommates]

        self.points = Decimal(sum(user_points))

        if len(countries) > 1:
            self.points += Decimal((self.COUNTRY_POINTS * len(countries)))

        if len(majors) > 1:
            self.points += Decimal((self.MAJOR_POINTS * len(majors)))

        if len(regions) > 1:
            self.points += Decimal((self.REGION_POINTS * len(regions)))

        # Add in the roommates
        if not ignore_roommates:
            for mate in self.roommates.all():
                mate.save(ignore_roommates=True)

    def save(self, ignore_roommates=False, **kwargs):

        # Save if not already
        if not self.pk:
            super(UserProfile, self).save()  # Call the "real" save() method.

        self.update_points(ignore_roommates)
        super(UserProfile, self).save()  # Call the "real" save() method.

    def __str__(self):
        if self.get_full_name():
            return self.get_full_name()
        else:
            return self.get_username()


class RoomManager(models.Model):
    pass


class Room(models.Model):
    ROOM_CODE_REGEX = r'[A-Z]{2}-\d{3}'

    SINGLE_ROOM_TAG = 'single'
    DOUBLE_ROOM_TAG = 'double'
    TRIPLE_ROOM_TAG = 'triple'
    TALL_ROOM_TAG = 'tall'
    QUIET_ROOM_TAG = 'quiet'
    DISABLED_ROOM_TAG = 'disabled'

    manager = RoomManager()

    # TODO Write format validator
    code = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=ROOM_CODE_REGEX,
                message='Enter a valid room code.'
            )]
    )

    college = CollegeField()

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

    def save(self, update_associated=False, **kwargs):
        # Save ourselves if we're not in the DB, so we can use m2m field
        if not self.pk:
            super(Room, self).save(kwargs)

        self.update_generated_tags()

        if update_associated:
            for room in self.associated.all():
                room.save(update_associated=False)

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
