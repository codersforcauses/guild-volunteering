from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import admin
from .adminForms import *
from .models import *
from django.db.models import F, Min, Max, ExpressionWrapper, Sum, fields
from django.http import HttpResponse

import csv
import datetime

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

def getFileName(user, organisation):
    if not user == None and not organisation == None:
        return organisation.name + "-" + user.user.username
    elif not user == None:
        return user.user.username
    elif not organisation == None:
        return organisation.name
    else:
        return "" #return an empty string

@admin.site.register_view(r'logbook/export/statistics', visible='true', name="Export Statistics")
def statisticsView(request):

    if request.method == 'POST':
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Guild_Volunteering_Stats.csv"'
        writer = csv.writer(response)
        
        writer.writerow(['No. Students This Year','No. Organisations'])
        num_orgs = len(Organisation.objects.all())
        num_students = len(LogEntry.objects.filter(start__year=datetime.datetime.now().year).values('book__user').distinct())
        print(num_students)
        writer.writerow([num_students,num_orgs])

        total_hrs = LogEntry.objects.filter(start__year=datetime.datetime.now().year,status="Approved"
                                            ).annotate(total_duration=Sum(ExpressionWrapper(F('end') - F('start'),  output_field=fields.DurationField()))
                                            ).aggregate(total_time = Sum('total_duration'))
        
        total_sec = total_hrs['total_time']
        total_hrs = total_sec.total_seconds()/3600.0
        writer.writerow(' ')
        writer.writerow(['Total Hrs/Yr'])
        writer.writerow([total_hrs])

        return response
    
    else:
        
        return render(request, 'admin/logbook/statistics.html',{})

@admin.site.register_view(r'logbook/export/logbooks', visible='false', name="Export Logbooks")
def exportView(request):
    DATE_FORMAT = '%d/%m/%Y'
    if request.method == 'POST':
        form = ExportForm(request.POST)
        
        if form.is_valid():
            
            response = HttpResponse(content_type='text/csv')
            user = form.cleaned_data['student']
            organisation = form.cleaned_data['organisation']
            
            response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(getFileName(user,organisation))
            writer = csv.writer(response)
            writer.writerow(['StudentID','First Name','Surname','Calendar Year','Position Type','Host Organisation Code','Host Organisation Description','Start Date','End Date','Hours'])

            fields = ['book__user__user__username', 'book__user__user__first_name','book__user__user__last_name', 'year', 'book__category__name', 'book__organisation__code','book__organisation__name']
            entries = []
            
            if not user == None and not organisation == None:
                entries = LogEntry.objects.filter(book__organisation__exact = organisation,book__user = user, status='Approved'
                    ).extra(select={'year': "EXTRACT(year FROM start)"}
                    ).values(*fields
                    ).annotate(startDate=Min('start'), endDate=Max('end'))
                print(entries)
            elif not user == None:
                entries = LogEntry.objects.filter(book__user = user,status='Approved'
                    ).extra(select={'year': "EXTRACT(year FROM start)"}
                    ).values(*fields
                    ).annotate(startDate=Min('start'), endDate=Max('end'))
            elif not organisation == None:
                entries = LogEntry.objects.filter(book__organisation = organisation,status='Approved'
                    ).extra(select={'year': "EXTRACT(year FROM start)"}
                    ).values(*fields
                    ).annotate(startDate=Min('start'), endDate=Max('end'))
            else:
                return(request, 'admin/logbook/export.html', {})
                
            for entry in entries:
                writer.writerow([entry[f] for f in fields]
                        + [ entry['startDate'].strftime(DATE_FORMAT), entry['endDate'].strftime(DATE_FORMAT), round((entry['endDate']-entry['startDate']).seconds/3600)])
            return response

    else:
        form = ExportForm()

    context = dict(admin.site.each_context(request),
        form=form)
    return render(request, 'admin/logbook/export.html',context)
