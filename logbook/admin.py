from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import admin
from .adminForms import *
from .models import *
from django.db.models import F, Min, Max

from django.http import HttpResponse
import csv

@admin.register(LBUser)
class LBUserAdmin(admin.ModelAdmin):
    list_display = ['user','first_name','last_name', 'email',]

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    def email(self,obj):
        return obj.user.email

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(LogBook)
class LogBookAdmin(admin.ModelAdmin):
    list_display = ['user','name','organisation','category','description','created_at','updated_at',]

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['book','description','supervisor','start','end',
                    'created_at','updated_at','status',]
@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    # Will need to add the Org's Calista code when we add that to model
    list_display = ['name','code']

@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ['user','email','validated','organisation',]

@admin.site.register_view(r'logbook/export', visible='false', name="Export Logbooks")
def exportView(request):
    DATE_FORMAT = '%d/%m/%Y'
    if request.method == 'POST':
        form = ExportForm(request.POST)
        if form.is_valid():
            response = HttpResponse(content_type='text/csv')
            user = form.cleaned_data['student']
            response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(user.user.username)
            writer = csv.writer(response)
            writer.writerow(['StudentID','First Name','Surname','Calendar Year','Position Type','Host Organisation Code','Host Organisation Description','Start Date','End Date','Hours'])
            fields = ['book__user__user__username', 'book__user__user__first_name','book__user__user__last_name', 'year', 'book__category__name', 'book__organisation__code','book__organisation__name']
            entries = LogEntry.objects.filter(book__user=user, status='Approved'
                    ).extra(select={'year': "EXTRACT(year FROM start)"}
                    ).values(*fields
                    ).annotate(startDate=Min('start'), endDate=Max('end'))
            print(entries)
            for entry in entries:
                print(entry,'\n', entry['year'])
                writer.writerow([entry[f] for f in fields]
                        + [ entry['startDate'].strftime(DATE_FORMAT), entry['endDate'].strftime(DATE_FORMAT), round((entry['endDate']-entry['startDate']).seconds/3600)])
            return response

    else:
        form = ExportForm()

    context = dict(admin.site.each_context(request),
        form=form)
    return render(request, 'admin/logbook/export.html',context)
