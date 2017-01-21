from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class LBUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    def __str__(self):
        return str(self.user)

class Organisation(models.Model):
    name = models.CharField(max_length=200)
    # more fields here once we get that email with the csv of organisations
    # UPDATE logbook.admin so org has calista code field in it
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

class LogBook(models.Model):
    user = models.ForeignKey(LBUser, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.user) + " - " + self.name
    readonly_fields = ('created_at','updated_at',)

#Category of the log entry
class Category(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return str(self.name)

class LogEntry(models.Model):
    book = models.ForeignKey(LogBook, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
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
