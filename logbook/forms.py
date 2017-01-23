from django import forms
from .models import *
from django.core.validators import RegexValidator
import re
studentNumRegex = re.compile(r'^[0-9]{8}$')

class StundetNumField(forms.CharField):
    default_validators = [RegexValidator(regex=studentNumRegex, message='Enter a valid student number')]
    widget = forms.TextInput(attrs={'class':'form-control', 'placeholder':'Student Number'}) # bootstrap class for styling

class SignupForm(forms.Form):
    studentNum = StundetNumField(label='')
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))
    passwordVerify = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password again'}))
    def validate(self):
        super().validate()
        if password == '':
            raise forms.ValidationError('Password cannot be empty')
        if password != passwordVerify:
            raise forms.ValidationError('Passwords do not match')
            
class LoginForm(forms.Form):
    studentNum = StundetNumField(label='')
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))

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
