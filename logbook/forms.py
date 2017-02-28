from django import forms
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import User
from django.contrib.admin import widgets  
from .models import *

import re
from datetimewidget.widgets import DateTimeWidget

studentNumRegex = re.compile(r'^[0-9]{8}$')

class StundetNumField(forms.CharField):
    default_validators = [RegexValidator(regex=studentNumRegex, message='Enter a valid student number')]
    widget = forms.TextInput(attrs={'class':'form-control', 'placeholder':'Student Number'}) # bootstrap class for styling

class EmailField(forms.CharField):
    default_validators = [EmailValidator()]
    widget = forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'})

class UsernameField(forms.CharField):
    widget = forms.TextInput(attrs={'class':'form-control', 'placeholder':'Student Number/Username'})

class FirstNameField(forms.CharField):
    widget = forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'})

class LastNameField(forms.CharField):
    widget = forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'})

class PasswordField(forms.CharField):
    widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'})

class SignupFormBase(forms.Form):
    username = forms.CharField() # have to declare here otherwise order of form elements will be weird
    first_name = forms.CharField()
    last_name = forms.CharField()
    password = PasswordField(label='')
    passwordVerify = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password Again'}))
    def clean(self):
        cleaned_data = super().clean()

        # Check that passwords match
        password = cleaned_data.get('password')
        passwordVerify = cleaned_data.get('passwordVerify')
        if password == '':
            raise forms.ValidationError('Password cannot be empty')
        if password != passwordVerify:
            raise forms.ValidationError('Passwords do not match')

        #check if user exists
        if User.objects.filter(username=cleaned_data.get('username')).exists():
            raise forms.ValidationError('User already exists')
        return cleaned_data

class SignupForm(SignupFormBase):
    username = StundetNumField(label='')
    first_name = FirstNameField(label='')
    last_name = LastNameField(label='')

class SupervisorSignupForm(SignupFormBase):
    username = EmailField(label='')
    first_name = FirstNameField(widget=forms.HiddenInput(), initial=None)
    last_name = LastNameField(widget=forms.HiddenInput(), initial=None)
            
class LoginForm(forms.Form):
    username = UsernameField(label='')
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))

class LogBookForm(forms.Form):
    bookOrganisation = forms.ModelChoiceField(queryset = Organisation.objects.all(), label='Organisation',help_text='<span data-toggle="tooltip" style="pading:20px" title="Please email Guild Volunteering if an organisation is not listed"><a>?</a></span>')                                              
    bookCategory = forms.ModelChoiceField(queryset = Category.objects.all(), label='Category',help_text='Choose a category that <strong>best</strong> describes your work.')
    bookName = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Book Name'}))
    bookDescription = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Book Description'}), required=False)

class LogEntryForm(forms.Form):
    description = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name'}))

    def __init__(self, *args, **kwargs):
        org_id = kwargs.pop('org_id')
        super(LogEntryForm,self).__init__(*args,**kwargs)
        # Allow user to select supervisor from a list of supervisors 
        self.fields['supervisor'].queryset = Supervisor.objects.filter(organisation = org_id)
        
    supervisor = forms.ModelChoiceField(queryset = [], label = 'Supervisor')
    
    dateTimeOptions = {
        'format': 'dd/mm/yyyy hh:ii:00',
        'weekStart' : '1',
        'autoclose': True,
        'showMeridian': True,
        'minuteStep' : '15',
        'clearBtn' : True,
        }
    start = forms.DateTimeField(widget=DateTimeWidget(usel10n=False,options = dateTimeOptions, bootstrap_version=3),label='',)
    end = forms.DateTimeField(widget=DateTimeWidget(usel10n=False,options = dateTimeOptions, bootstrap_version=3),label='',)        

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        if start != None or end != None:
            timediff = end-start
            if timediff.total_seconds() < 0:
                raise forms.ValidationError('Invalid start or end time')
        
        return cleaned_data

class EditNamesForm(forms.ModelForm):
    first_name = FirstNameField()
    last_name = FirstNameField()

    class Meta:
        model = User
        fields = ['first_name','last_name',]

class DeleteUserForm(forms.ModelForm):
    is_active = forms.BooleanField(label='', initial=False)
    
    class Meta:
        model = User
        fields = ['is_active']

    def __init__(self, *args, **kwargs):
        super(DeleteUserForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].help_text = "Check this box if you are sure you want to suspend this account."

    def clean_is_active(self):  
        # Reverses true/false for your form prior to validation
        is_active = not(self.cleaned_data["is_active"])
        return is_active
