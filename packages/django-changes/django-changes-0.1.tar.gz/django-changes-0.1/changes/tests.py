import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.tests.utils import skipIfCustomUser

from models import Change


@skipIfCustomUser
class ChangesTestCase(TestCase):
    def setUp(self):
        self.actor = User.objects.create(username='actor')
        self.subject = User.objects.create(username='subject')

    def test_add_get_change_for_object(self):
        when = datetime.datetime(1984, 11, 15, 10)
        c1 = Change.objects.add_change_for_object(self.subject, who=self.actor,
                                                 why='Test', when=when)
        c2 = Change.objects.add_change_for_object(self.subject)
        self.assertEqual(c1.who, self.actor)
        self.assertEqual(c1.c_obj, self.subject)
        self.assertEqual(c1.when, when)

        self.assertEqual(
            [],
            list(Change.objects.get_changes_for_object(self.actor))
        )
        self.assertEqual(
            [c1, c2],
            list(Change.objects.get_changes_for_object(self.subject))
        )
        self.assertEqual(
            [c1],
            list(Change.objects.get_changes_by_user(self.actor))
        )
        self.assertEqual(
            [c2],
            list(Change.objects.get_anonymous_changes())
        )
