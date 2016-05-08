from django.test import TestCase
from roomer.models import UserProfile


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
            country='Indie',
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

        code = a.send_roommate_request(b)

        self.assertEqual(UserProfile.REQUEST_SENT, code)

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
