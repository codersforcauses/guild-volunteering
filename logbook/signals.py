import django.db.models.signals as signals
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import LBUser

"""
#https://docs.djangoproject.com/en/1.10/ref/signals/#post-save
@receiver(signals.post_save, sender=User)
def user_saved(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        LBUser.objects.create(user=instance)
    try:
        instance.lbuser.save()
    except:
        pass
"""
