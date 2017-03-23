from django import forms
from django.core.exceptions import ValidationError

from .models import *

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
