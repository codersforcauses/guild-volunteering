from django.contrib import admin
from .models import *

# These only have one field
for model in [LBUser, Category]:
    admin.site.register(model)

class LogBookAdmin(admin.ModelAdmin):
    list_display = ['user','name','description','created_at','updated_at',]

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['book','category','description','supervisor','start','end',
                    'created_at','updated_at','status',]

class OrganisationAdmin(admin.ModelAdmin):
    # Will need to add the Org's Calista code when we add that to model
    list_display = ['name',]

class SupervisorAdmin(admin.ModelAdmin):
    list_display = ['email','user','validated','organisation',]

admin.site.register(LogBook, LogBookAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Supervisor, SupervisorAdmin)
