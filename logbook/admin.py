from django.contrib import admin
from .models import *

for model in [LBUser, Organisation, Supervisor, LogBook, Category, LogEntry]:
    admin.site.register(model)
