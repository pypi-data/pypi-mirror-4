from django.test import TestCase
from django.contrib.auth.models import User, Group

from . import record
import models

class JournalTestCase(TestCase):
    def setUp(self):
        self.users = []
        self.groups = []
        for i in range(20):
            self.users.append(
                    User.objects.create(username='user%s' % i))
        for i in range(20):
            self.groups.append(
                    Group.objects.create(name='group%s' % i))
        for i in range(20):
            record('login', '{user} logged in', user=self.users[i])
        for i in range(20):
            record('group-changed', '{user1} gave group {group} to {user2}',
                    user1=self.users[i], group=self.groups[i], 
                    user2=self.users[(i+1) % 20])
        for i in range(20):
            record('logout', '{user} logged out', user=self.users[i])

    def test_count(self):
        self.assertEqual(models.Journal.objects.count(), 60)

    def test_login(self):
        for i, event in zip(range(20), models.Journal.objects.for_tag('login')):
            self.assertEqual(unicode(event), 'user{0} logged in'.format(i))

    def test_groups(self):
        for i, event in zip(range(40), models.Journal.objects.for_tag('group-changed')):
            self.assertEqual(unicode(event),
                    'user{0} gave group group{0} to user{1}'.format(i, (i+1)%20))

    def test_logout(self):
        for i, event in zip(range(20), models.Journal.objects.for_tag('logout')):
            self.assertEqual(unicode(event), 'user{0} logged out'.format(i))

