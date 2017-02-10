from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User, Group
from ..models import *
from ..forms import *

def makeBookName(i):
    return 'Book {}'.format(i)

class TestBooks(TestCase):
    def setUp(self):
        user = User.objects.create_user('11111111', '11111111@student.uwa.edu.au', 'password')
        user.save()
        group = Group.objects.get(name='LBStudent')
        group.user_set.add(user)
        group.save()

        self.user = LBUser.objects.get(user=user)
        self.client.cookies = self.client.post(reverse('logbook:login'), {'username':'11111111', 'password':'password'}).cookies

        self.books = []
        for i in range(6):
            self.books.append(LogBook.objects.create(user=self.user, name=makeBookName(i), description=makeBookName(i)))

    def pages_reachable(self):
        response = self.client.get(reverse('logbook:list'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('logbook:create'))
        self.assertEqual(response.status_code, 200)

    def test_view_books(self):
        response = self.client.get(reverse('logbook:list'), {})
        for i in range(len(self.books)):
            self.assertContains(response, makeBookName(i))

    def test_add_book(self):
        response = self.client.post(reverse('logbook:create'), {'bookName':makeBookName(len(self.books)+1), 'bookDescription':makeBookName(len(self.books)+1)}, follow=True)
        self.assertContains(response, makeBookName(len(self.books)+1))

    def test_delete_book(self):
        response = self.client.post(reverse('logbook:list'), {'model_selected':[self.books[0].id], 'selectedAction':'delete'}, follow=True)
        self.assertNotContains(response, makeBookName(0))

    def test_delete_books(self):
        response = self.client.post(reverse('logbook:list'), {'model_selected':[b.id for b in self.books[1:3]], 'selectedAction':'delete'}, follow=True)
        self.assertNotContains(response, makeBookName(1))
        self.assertNotContains(response, makeBookName(2))
