#Django imports
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, mail_admins
from django.template import Context,Template
from django.core.validators import RegexValidator, EmailValidator
from django.urls import reverse

#Logbook app imports
from .models import *
from django.conf import settings

# Added apps
from datetimewidget.widgets import DateTimeWidget
from dal import autocomplete

#General imports
import os
import re
import socket

studentNumRegex = re.compile(r'^[0-9]{8}$')

#Checks to see if the student number entered on account creation match
#the required regex.
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

    def save(self, data):
        user = User.objects.create_user(data['username'],
                                        data['username'] + '@student.uwa.edu.au',
                                        data['password'])

        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.is_active = False
        group = Group.objects.get(name='LBStudent')
        group.user_set.add(user)
        group.save()
        user.save()
        lbUser = LBUser()
        lbUser.user = user
        #Below sets the key which much be in the link a user sends, and how long until it will expire.
        lbUser.activation_key = data['activation_key']
        lbUser.key_expires = datetime.datetime.strftime(datetime.datetime.now()+ datetime.timedelta(days=settings.DAYS_VALID), "%Y-%m-%d %H:%M:%S")
        lbUser.save()
        return user

    #Used for account creation, where users must verify their email address by clicking link.
    def sendVerifyEmail(self, mailData):
        hostname = socket.gethostbyname(socket.gethostname())
        link = "http://"+hostname+":8000/logbook/activate/"+mailData['activation_key']
        contxt = Context({'activation_link':link,'username':mailData['username'],'first_name':mailData['first_name']})
        EMAIL_PATH = os.path.join(settings.BASE_DIR,'logbook','static', mailData['email_path'])
        file = open(EMAIL_PATH,'r')
        temp = Template(file.read())
        file.close
        message = temp.render(contxt)
        send_mail(mailData['email_subject'],message,'Guild Volunteering <volunteering@guild.uwa.edu.au>',[mailData['email']], fail_silently=False)

#May not be needed as supervisors either added by Guild Volunteering
#Or students create an unverified account in the log entry.
class SupervisorSignupForm(SignupFormBase):
    username = EmailField(label='')
    first_name = FirstNameField(widget=forms.HiddenInput(), initial=None)
    last_name = LastNameField(widget=forms.HiddenInput(), initial=None)
            
class LoginForm(forms.Form):
    username = UsernameField(label='')
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))

class EditLogBookForm(forms.Form):
    #Students are not allowed to edit the organisation for this logbook, as all the supervisors listed are from that org!
    name = forms.CharField(label='',required=True,widget=forms.TextInput(attrs={'class':'form-control', 'id':'edit_form_name', 'placeholder':'Book Name'}))
    category = forms.ModelChoiceField(required=True,queryset = Category.objects.all().order_by('name'),empty_label='Volunteer Category...',
                                          label='',widget=forms.Select(attrs={'class':'form-control','id':'edit_form_category'}))
    
class LogBookForm(forms.Form):
    bookName = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Book Name'}))
    bookOrganisation = forms.ModelChoiceField(queryset = Organisation.objects.all().order_by('name'), label='', empty_label='Choose Organisation...',
                                              widget=forms.Select(attrs={'class':'form-control'}),
                                              help_text='<span data-toggle="tooltip" style="pading:20px" title="Please email Guild Volunteering if an organisation is not listed"><a>?</a></span>')                                              

    bookCategory = forms.ModelChoiceField(queryset = Category.objects.all().order_by('name'), empty_label='Select Volunteer Category...', label='',
                                          widget=forms.Select(attrs={'class':'form-control'}),
                                          help_text='Choose a category that <strong>best</strong> describes your work.')
    

class EditLogEntryForm(forms.Form):
    name = name = forms.CharField(label='',required=True, widget=forms.TextInput(attrs={'class':'form-control',
                                            'id':'edit_form_name','placeholder':'Name Log Entry'}))

    def __init__(self, *args, **kwargs):
        org_id = kwargs.pop('org_id')
        super(EditLogEntryForm,self).__init__(*args,**kwargs)
        # Allow user to select supervisor from a list of supervisors 
        self.fields['supervisor'].queryset = Supervisor.objects.filter(organisation = org_id).order_by('user__username')
        self.fields['supervisor'].empty_label = 'Select Supervisor...'
        
    supervisor = forms.ModelChoiceField(queryset = [], label='', widget=forms.Select(attrs={'class':'form-control','id':'edit_form_supervisor'}))
    dateTimeOptions = {
        'format': 'dd/mm/yyyy hh:ii:00',
        'weekStart' : '1',
        'autoclose': True,
        'showMeridian': True,
        'minuteStep' : '15',
        'clearBtn' : True,
        }
    
    start = forms.DateTimeField(widget=DateTimeWidget(usel10n=False,options = dateTimeOptions, bootstrap_version=3, attrs={'id':'edit_form_start'}),label='',)
    end = forms.DateTimeField(widget=DateTimeWidget(usel10n=False,options = dateTimeOptions, bootstrap_version=3,attrs={'class':'form-control','id':'edit_form_end','read-only':''}),label='',) 

    def clean(self):
        cleaned_data = super().clean()
        
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        if start != None or end != None:
            timediff = end-start
            if timediff.total_seconds() < 0:
                raise ValidationError('Invalid start or end time')
        
        return cleaned_data

class LogEntryForm(forms.Form):
    name = forms.CharField(label='',required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name Log Entry'}))

    def __init__(self, *args, **kwargs):
        org_id = kwargs.pop('org_id')
        super(LogEntryForm,self).__init__(*args,**kwargs)
        # Allow user to select supervisor from a list of supervisors 
        self.fields['supervisor'].queryset = Supervisor.objects.filter(organisation = org_id).order_by('user__username')
        self.fields['supervisor'].empty_label = 'Select Supervisor...'
        
    supervisor = forms.ModelChoiceField(queryset = [], label='', widget=forms.Select(attrs={'class':'form-control'}))
    
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
                raise ValidationError('Invalid start or end time')
        
        return cleaned_data

#Creates an unverified supervisor
class TempSupervisorForm(forms.Form):
    email = EmailField(label='')

    def clean(self):
        cleaned_data = super().clean()
        if len(Supervisor.objects.filter(email = cleaned_data['email'])) > 0:
            raise ValidationError('Supervisor exists in the system.')
        
        return cleaned_data
    
    #!!IMPORTANT!! GUILD MUST MUST MUST set the supervisor to the supervisor group
    #when adding the supervisor account otherwise will get an error page.
    def save(self, data):
        suprvisr = Supervisor()
        suprvisr.email = data['supervisor_email']
        suprvisr.validated = False
        suprvisr.organisation = data['organisation']
        suprvisr.user = None
        suprvisr.save()
        
        return suprvisr

    #As with account creation it will send an email to the guild to look up this
    #Supervisor and verify them or not.
    def sendMail(self, mailData):
        hostname = socket.gethostbyname(socket.gethostname())
        #link = "http://"+hostname+":8000/logbook/activate/"+mailData['activation_key']
        contxt = Context({'supervisor_email':mailData['supervisor_email'],'organisation':mailData['organisation']})
        EMAIL_PATH = os.path.join(settings.BASE_DIR,'logbook','static', mailData['email_path'])
        file = open(EMAIL_PATH,'r')
        temp = Template(file.read())
        file.close
        message = temp.render(contxt)
        mail_admins(mailData['email_subject'],message,fail_silently=False)

#Allows a logged in user to edit their first and last name, they entered.
class EditNamesForm(forms.ModelForm):
    first_name = FirstNameField(label='')
    last_name = LastNameField(label='')

    class Meta:
        model = User
        fields = ['first_name','last_name',]

#Suspends a users account so that their logbooks are kept in the database
#but they cant log in, will need to see about th rules regarding deleting accounts.
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

"""
Below forms SetPasswordForm and ChangePasswordForm are taken directly
from the django documentation except I've flipped the position of the
old_password and altering the placeholders and attrs{} of the password fields.
"""
class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch':("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))
    new_password2 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password Again'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'],code='password_mismatch',)
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': ("Your old password was entered incorrectly. Please enter it again."),})
    old_password = forms.CharField(label='',widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Old Password'}))

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(self.error_messages['password_incorrect'],code='password_incorrect',)
        return old_password

class SearchBarForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Search'}),
                            label='',required = True)
    
