from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User, Group
from ..models import *
from ..forms import *

def makeEntryName(i):
    return 'Entry {}'.format(i)

class TestEntries(TestCase):
    def setUp(self):
        user = User.objects.create_user('11111111', '11111111@student.uwa.edu.au', 'password')
        user.save()
        group = Group.objects.get(name='LBStudent')
        group.user_set.add(user)
        group.save()

        self.user = LBUser.objects.get(user=user)
        self.client.cookies = self.client.post(reverse('logbook:login'), {'username':'11111111', 'password':'password'}).cookies

        self.book = LogBook.objects.create(user=self.user, name='book', description='book')
        self.entries = []
        for i in range(6):
            self.entries.append(LogEntry.objects.create(book=self.book, description=makeEntryName(i), start='2017-01-01 00:00:00', end='2017-01-01 00:00:00'))

    def pages_reachable(self):
        response = self.client.get(reverse('logbook:view', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('logbook:add_entry', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_entries(self):
        response = self.client.get(reverse('logbook:view', args=[self.book.id]), {})
        for i in range(len(self.entries)):
            self.assertContains(response, makeEntryName(i))

    def test_add_entry(self):
        response = self.client.post(reverse('logbook:add_entry', args=[self.book.id]), {'description':makeEntryName(len(self.entries)+1), 'start':'2017-01-01 00:00:00', 'end':'2017-01-01 00:00:00'}, follow=True)
        self.assertContains(response, makeEntryName(len(self.entries)+1))

    def test_delete_entry(self):
        response = self.client.post(reverse('logbook:view', args=[self.book.id]), {'model_selected':[self.entries[0].id], 'selectedAction':'delete'}, follow=True)
        self.assertNotContains(response, makeEntryName(0))

    def test_delete_books(self):
        response = self.client.post(reverse('logbook:view', args=[self.book.id]), {'model_selected':[e.id for e in self.entries[1:3]], 'selectedAction':'delete'}, follow=True)
        self.assertNotContains(response, makeEntryName(1))
        self.assertNotContains(response, makeEntryName(2))
