"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime
from django.test import TestCase
from django.utils.timezone import utc

from last_used import use, get, LIMIT
from last_used.models import LastUsed, User


class TestUse(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')

    def test_use(self):

        obj = use(self.user, self.user)

        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.content_object, self.user)

    def test_use_key(self):

        obj = use(self.user, self.user, key="some_key")

        self.assertEqual(obj.key, "some_key")
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.content_object, self.user)

    def test_use_when(self):
        when = datetime.datetime(2000, 1, 1, 4, 3, 2, 1).replace(tzinfo=utc)
        obj = use(self.user, self.user, when=when)

        self.assertEqual(obj.last_used, when)
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.content_object, self.user)

    def test_use_delete(self):

        for i in range(LIMIT + 2):
            use(self.user, self.user)

        self.assertEqual(LastUsed.objects.count(), LIMIT)

    def test_use_keys(self):

        for i in range(LIMIT + 2):
            use(self.user, self.user, key=str(i))

        self.assertEqual(LastUsed.objects.count(), LIMIT + 2)


class TestGet(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')

    def test_empty(self):

        objs = get(self.user, self.user)

        self.assertEqual(objs.count(), 0)

    def test_found(self):

        last_used = LastUsed.objects.create(user=self.user,
                                        content_object=self.user)
        objs = list(get(User, self.user))

        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], last_used)

    def test_limit(self):

        for i in range(4):
            LastUsed.objects.create(user=self.user, content_object=self.user)

        objs = list(get(self.user, self.user, limit=2))

        self.assertEqual(len(objs), 2)

    def test_no_model(self):

        objs = get(user=self.user)

        self.assertEqual(objs.count(), 0)

    def test_no_user(self):

        objs = get(model=self.user)

        self.assertEqual(objs.count(), 0)

    def test_with_key(self):

        objs = get(key="some_key")

        self.assertEqual(objs.count(), 0)


class TestModel(TestCase):

    def test_unicode_no_key(self):
        user = User(username="test_user")
        last_used = LastUsed(content_object=user, user=user)

        self.assertIn(unicode(user), unicode(last_used))

    def test_unicode_key(self):
        user = User(username="test_user")
        last_used = LastUsed(content_object=user, user=user, key="key_test")

        self.assertIn(unicode(user), unicode(last_used))
        self.assertIn("key_test", unicode(last_used))
