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
