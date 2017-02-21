from django import template

register = template.Library()

import datetime

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
