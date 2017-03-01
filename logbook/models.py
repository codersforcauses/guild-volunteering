from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import datetime

class LBUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    activation_key = models.CharField(max_length=64)
    key_expires = models.DateTimeField(default=datetime.datetime.now()+datetime.timedelta(days=7))
    def __str__(self):
        return str(self.user)

class Organisation(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=8, blank=True, default=None)
    def __str__(self):
        return str(self.name)

class Supervisor(models.Model):
    email = models.EmailField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, default=None)
    validated = models.BooleanField(default=False)
    # organisation is nullable because some supervisors might not belong to an organisation, or haven't been assigned one yet
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, default=None)
    def __str__(self):
        return str(self.email)

class Category(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return str(self.name)

class LogBook(models.Model):
    user = models.ForeignKey(LBUser, on_delete=models.PROTECT)
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, default=None )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, default=None)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.user) + " - " + self.name
    readonly_fields = ('created_at','updated_at',)

class LogEntry(models.Model):
    book = models.ForeignKey(LogBook, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True)
    start = models.DateTimeField('task start')
    end = models.DateTimeField('task end')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    UNAPPROVED = 'Unapproved'
    PENDING = 'Pending'
    APPROVED = 'Approved'
    STATUS_CHOICES = (
        # Has not been submitted for approval or was denied (use last modified time).
            (UNAPPROVED, 'Unapproved'),
            (PENDING, 'Pending'), # Awaiting approval.
            (APPROVED, 'Approved'), # Supervisor has approved the log entry.
        )
    status = models.CharField(choices = STATUS_CHOICES, max_length = 15, default = UNAPPROVED)
    def __str__(self):
        return str(self.book) + " - " + self.description
    readonly_fields = ('created_at','updated_at',)
