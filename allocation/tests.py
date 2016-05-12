from django.test import TestCase
from unittest import expectedFailure
from roomer.models import UserProfile, Room, UserPreference
from .utils import get_cost_matrix, get_hungarian, get_dict_from_key_in_list


# Create your tests here.

class TestHungarian(TestCase):
    def setUp(self):
        """
        self.basic_cost_matrix = [[82, 83, 69, 92], [77, 37, 49, 92], [11, 69, 5, 86], [8, 9, 98, 23]]
        self.basic_hungarian_result = [69, 37, 11, 23]
        # Basically Leo
        UserProfile.objects.create(
            username='a',
            seniority=2,
            year=17,
            major='Computer Science',
            country='Germany',
            old_college='NM',
            college='ME',
        )

        # Basically Sid
        UserProfile.objects.create(
            username='b',
            seniority=3,
            year=16,
            major='Computer Science',
            country='India',
            old_college='ME',
            college='ME',
        )

        # Basically a mover
        UserProfile.objects.create(
            username='c',
            seniority=1,
            year=18,
            major='Physics',
            country='Albania',
            old_college='NM',
            college='ME',
        )

        # Basically a Nordie freshie
        UserProfile.objects.create(
            username='d',
            seniority=1,
            year=18,
            major='Chemistry',
            country='Albania',
            old_college='NM',
            college='NM',
        )

        user_a = UserProfile.objects.get(username='a')
        user_b = UserProfile.objects.get(username='b')
        user_c = UserProfile.objects.get(username='c')
        user_d = UserProfile.objects.get(username='d')
        # user_a.send_roommate_request(user_b)
        # user_b.inbox.first().accept()

        room_a, _ = Room.objects.get_or_create(
            college='ME',
            floor=3,
            block='A',
            code='MA-303'
        )
        room_a.save()
        room_b, _ = Room.objects.get_or_create(
            college='ME',
            floor=2,
            block='A',
            code='MA-203'
        )
        room_b.save()
        room_c, _ = Room.objects.get_or_create(
            college='NM',
            floor=3,
            block='B',
            code='NB-351'
        )
        room_c.save()
        room_d, _ = Room.objects.get_or_create(
            college='ME',
            floor=3,
            block='C',
            code='MC-104'
        )
        room_d.save()
        room_e, _ = Room.objects.get_or_create(
            college='NM',
            floor=3,
            block='B',
            code='NA-350'
        )
        room_e.save()

        # room_a.associated.add(room_b)

        UserPreference.objects.create(
            preference_level=1,
            user=user_a,
            room=room_b
        )
        UserPreference.objects.create(
            preference_level=2,
            user=user_a,
            room=room_d
        )
        UserPreference.objects.create(
            preference_level=1,
            user=user_b,
            room=room_a
        )
        UserPreference.objects.create(
            preference_level=2,
            user=user_b,
            room=room_d
        )
        UserPreference.objects.create(
            preference_level=1,
            user=user_c,
            room=room_d
        )
        UserPreference.objects.create(
            preference_level=2,
            user=user_c,
            room=room_a
        )
        UserPreference.objects.create(
            preference_level=1,
            user=user_d,
            room=room_c
        )
        UserPreference.objects.create(
            preference_level=2,
            user=user_d,
            room=room_e
        )

        self.pref_a = UserPreference.objects.get(user=user_a, preference_level=1)
        self.pref_b = UserPreference.objects.get(user=user_b, preference_level=1)
        self.pref_c = UserPreference.objects.get(user=user_c, preference_level=1)
        self.pref_d = UserPreference.objects.get(user=user_d, preference_level=1)
        """

    @expectedFailure
    def test_basic_hungarian(self):
        result = get_cost_matrix(self.basic_cost_matrix)
        self.assertEqual(result, self.basic_hungarian_result)

    @expectedFailure
    def test_hungarian_on_users(self):
        allocations = get_hungarian()
        self.assertEqual(
            get_dict_from_key_in_list("user", {"user_id": UserProfile.objects.get(username="b").id}, allocations)[
                "preference"], self.pref_b.preference_level)
