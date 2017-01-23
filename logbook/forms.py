from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

from .models import *

import re

studentNumRegex = re.compile(r'^[0-9]{8}$')

class StundetNumField(forms.CharField):
    default_validators = [RegexValidator(regex=studentNumRegex, message='Enter a valid student number')]
    widget = forms.TextInput(attrs={'class':'form-control', 'placeholder':'Student Number'}) # bootstrap class for styling

class PasswordField(forms.CharField):
    widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'})

class SignupForm(forms.Form):
    studentNum = StundetNumField(label='')
    password = PasswordField(label='')
    passwordVerify = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password Again'}))
    def clean(self):
        cleaned_data = super().clean()
        # Check if user exists
        if User.objects.filter(username=cleaned_data.get('studentNum')).exists():
            raise forms.ValidationError('User already exists')
        # Check that passwords match
        password = cleaned_data.get('password')
        passwordVerify = cleaned_data.get('passwordVerify')
        if password == '':
            raise forms.ValidationError('Password cannot be empty')
        if password != passwordVerify:
            raise forms.ValidationError('Passwords do not match')
            
class LoginForm(forms.Form):
    studentNum = StundetNumField(label='')
    password = PasswordField(label='')

class LogBookForm(forms.Form):
    bookName = forms.CharField(label='')
    bookDescription = forms.CharField(label='')

class LogEntryForm(forms.Form):
    category = forms.ModelChoiceField(queryset = Category.objects.all())
    description = forms.CharField(label = '')
    # Allow user to select supervisor from a list of supervisors 
    supervisor = forms.ModelChoiceField(widget = forms.HiddenInput(), queryset = Supervisor.objects.all())
    start = forms.DateTimeField()
    end = forms.DateTimeField()
