from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import send_mass_mail

from .models import *

class StudentEmailForm(forms.Form):
    subject = forms.CharField(label='', required=True,
                              widget=forms.TextInput(attrs={'placeholder':'Subject',
                                                                     'class':'form-control'}))
    message = forms.CharField(label='',required=True,
                              widget=forms.Textarea(attrs={'placeholder':'Message'}))
    unfinalised = forms.BooleanField(label='',help_text='Select if you want to send send this email to students with un-finalised log hours', required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        
        message = cleaned_data['message']
        if len(message) == 0:
            raise ValidationError('Please enter a body to the message.')

        return cleaned_data

    def sendMail(self, emailData):
        data = (
            (emailData['subject'],emailData['message'],
             'Guild Volunteering <volunteering@guild.uwa.edu.au>',emailData['mail_list']),
            )
        send_mass_mail(data,fail_silently=False)

class SupervisorEmailForm(forms.Form):
    subject = forms.CharField(label='', required=True,
                              widget=forms.TextInput(attrs={'placeholder':'Subject',
                                                                     'class':'form-control'}))
    message = forms.CharField(label='',required=True,
                              widget=forms.Textarea(attrs={'placeholder':'Message'}))
    unapproved = forms.BooleanField(label='',help_text='Select if you want to send send this email to supervisors with un-approved log hours', required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        
        message = cleaned_data['message']
        if len(message) == 0:
            raise ValidationError('Please enter a body to the message.')

        return cleaned_data

    def sendMail(self, emailData):
        data = (
            (emailData['subject'],emailData['message'],
             'Guild Volunteering <volunteering@guild.uwa.edu.au>',emailData['mail_list']),
            )
        send_mass_mail(data,fail_silently=False)

class ExportForm(forms.Form):
    organisation = forms.ModelChoiceField(queryset = Organisation.objects.all().order_by('name'),
                                          label='',empty_label='Select Organisation...',widget=forms.Select(attrs={'class':'form-control'}), required=False)
    student = forms.ModelChoiceField(queryset = LBUser.objects.filter(user__groups__name='LBStudent').all().order_by('user__username'),
                                     label='',empty_label='Select Student Number...',widget=forms.Select(attrs={'class':'form-control'}), required=False)

    #Removed check, will export all organisations and all logbooks into a zip file.
    """
    def clean(self):
        cleaned_data = super().clean()

        org = cleaned_data.get('organisation')
        studnt = cleaned_data.get('student')

        if org == None and studnt == None:
            raise ValidationError('You must select at least one!')

        return cleaned_data
    """
