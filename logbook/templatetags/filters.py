from django import template

#Required call
register = template.Library()

import datetime

"""
Custom filter to convert timedelta object being presented to the supervisor
into the total minutes and hours which require approval.
"""
@register.filter(name='timedelta')
def timedelta(value):
    seconds = value.total_seconds()
    hours = int(seconds/3600.0)
    minutes = int((seconds - (hours*3600))/60.0)
    
    if hours == 0:
        return str(minutes) + ' minutes'
    elif minutes == 0:
        return str(hours) + ' hours'
    
    return str(hours) + ' hours ' + 'and ' + str(minutes) + ' minutes'

"""
Custom filter which removes all text after '@' for the supervisor email address,
reduces cluttering of the table on smaller devices.
"""
@register.filter(name="email")
def email(value):
    return str(value).split('@')[0]
