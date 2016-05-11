from django.test import TestCase
from roomer.models import UserProfile, RoommateRequest


class UserProfileTestCase(TestCase):
    def setUp(self):
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

    def test_roommates_get_added(self):
        a = UserProfile.objects.get(username='a')
        b = UserProfile.objects.get(username='b')

        code, new_request = a.send_roommate_request(b)

        self.assertEqual(UserProfile.REQUEST_SENT, code)
        self.assertIsInstance(new_request, RoommateRequest)

        self.assertEqual(new_request.sender, a)
        self.assertEqual(new_request.receiver, b)

        b.inbox.first().accept()

        self.assertSequenceEqual(b.roommates.all(), [a])
        self.assertSequenceEqual(a.roommates.all(), [b])

    def test_add_indirect_roommates(self):
        a = UserProfile.objects.get(username='a')
        b = UserProfile.objects.get(username='b')
        c = UserProfile.objects.get(username='c')

        a.send_roommate_request(b)
        b.inbox.first().accept()

        a.send_roommate_request(c)
        c.inbox.first().accept()

        self.assertSequenceEqual(a.roommates.all(), [b, c])
        self.assertSequenceEqual(b.roommates.all(), [a, c])
        self.assertSequenceEqual(c.roommates.all(), [a, b])

    def test_points_no_roommates_1(self):
        a = UserProfile.objects.get(username='a')
        a.save()

        self.assertEqual(2, a.points)

    def test_points_no_roommates_2(self):
        b = UserProfile.objects.get(username='b')
        b.save()

        self.assertEqual(3.5, b.points)

    def test_points_no_roommates_3(self):
        c = UserProfile.objects.get(username='c')
        c.save()

        self.assertEqual(1, c.points)

    def test_points_1_roommate(self):
        a = UserProfile.objects.get(username='a')
        b = UserProfile.objects.get(username='b')

        a.send_roommate_request(b)

        b.inbox.first().accept()
        a.save()  # Required for updating points
        b.save()

        self.assertEqual(8.5, b.points)
        self.assertEqual(8.5, a.points)

    def test_points_2_roommates(self):
        a = UserProfile.objects.get(username='a')
        b = UserProfile.objects.get(username='b')
        c = UserProfile.objects.get(username='c')

        a.send_roommate_request(b)
        b.inbox.first().accept()

        a.send_roommate_request(c)
        c.inbox.first().accept()

        a.save()
        b.save()
        c.save()

        self.assertEqual(12, a.points)
        self.assertEqual(12, b.points)
        self.assertEqual(12, c.points)

