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
