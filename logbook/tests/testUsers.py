from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User, Group
from ..models import *
from ..forms import *

class TestUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('11111111', '11111111@student.uwa.edu.au', 'password')
        cls.user.save()
        group = Group.objects.get(name='LBStudent')
        group.user_set.add(cls.user)
        group.save()

    def pages_reachable(self):
        response = self.client.get(reverse('logbook:signup'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('logbook:login'))
        self.assertEqual(response.status_code, 200)

    def test_signup_with_valid_input(self):
        response = self.client.post(reverse('logbook:signup'), {'username':'12345678', 'password':'password', 'passwordVerify':'password'})
        self.assertRedirects(response, reverse('logbook:login'))

    def test_signup_with_bad_student_number(self):
        response = self.client.post(reverse('logbook:signup'), {'username':'notAStudentNumber', 'password':'password', 'passwordVerify':'password'})
        self.assertFormError(response, 'signupForm', 'username', 'Enter a valid student number')

    def test_signup_with_mismatched_passwords(self):
        response = self.client.post(reverse('logbook:signup'), {'username':'12345678', 'password':'password1', 'passwordVerify':'password2'})
        self.assertFormError(response, 'signupForm', None, 'Passwords do not match')

    def test_signup_with_existing_user(self):
        response = self.client.post(reverse('logbook:signup'), {'username':'11111111', 'password':'password', 'passwordVerify':'password'})
        self.assertFormError(response, 'signupForm', None, 'User already exists')

    def test_login_valid(self):
        response = self.client.post(reverse('logbook:login'), {'username':'11111111', 'password':'password'})
        self.assertRedirects(response, reverse('logbook:index'))
