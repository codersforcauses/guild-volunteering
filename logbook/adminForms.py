from django import forms
from .models import *

class ExportForm(forms.Form):
    student = forms.ModelChoiceField(queryset = LBUser.objects.filter(user__groups__name='LBStudent').all(), label='Student')
    #organisation = forms.ModelChoiceField(queryset = Organisation.objects.all(), label='Organisation')

