from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import admin
from .adminForms import *
from .models import *
from django.db.models import F, Min, Max, ExpressionWrapper, Sum, fields
from django.http import HttpResponse

import csv
import datetime
import io
import zipfile

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
    list_display = ['user','name','organisation','category','exported','finalised','active','created_at','updated_at',]

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['book','name','supervisor','start','end','status',
                    'created_at','updated_at',]
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
        return "All Organisations"

def get_total_hrs(time):
    return int(time.total_seconds()/3600.0)

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

        total_hrs = LogEntry.objects.filter(start__year=datetime.datetime.now().year,status="Approved", supervisor__validated =  True
                                            ).annotate(total_duration=Sum(ExpressionWrapper(F('end') - F('start'),  output_field=fields.DurationField()))
                                            ).aggregate(total_time = Sum('total_duration'))
        
        total_hrs = get_total_hrs(total_hrs['total_time'])

        submitted_hrs = LogEntry.objects.filter(start__year=datetime.datetime.now().year,status="Approved", supervisor__validated = True, book__finalised = True
                                            ).annotate(total_duration=Sum(ExpressionWrapper(F('end') - F('start'),  output_field=fields.DurationField()))
                                            ).aggregate(total_time = Sum('total_duration'))
        calista_hrs = get_total_hrs(submitted_hrs['total_time'])
        writer.writerow(' ')
        writer.writerow(['Total Hrs This Yr','Submitted Hrs This Yr'])
        writer.writerow([total_hrs,calista_hrs])

        return response
    
    else:
        
        return render(request, 'admin/logbook/statistics.html',{'unexported_entries':getNumUnexported()})

@admin.site.register_view(r'logbook/clear_finalised_logbooks', visible='true', name='Clear Finalised Books')
def clearLogBooksView(request):
    if request.method == 'POST':
        logbooks = LogBook.objects.filter(finalised = True, active = True, exported=True)
        for book in logbook:
            book.active = False
            book.save
            
        #Redirect to a completed action page.
        return render(request, 'admin/logbook/action_complete.html',{'unexported_entries':getNumUnexported})
    else:
        return render(request, 'admin/logbook/clear_finalised_logbooks.html', {'unexported_entries':getNumUnexported})

#Function which simply tells views how many log entries havent been exported yet.
def getNumUnexported():
    return len(LogEntry.objects.filter(book__finalised = True, book__active = True, book__exported = False))

#Function that sets all the lobgooks which were exported to 'True'
def setExported(entries):
    """
    Find all distinct books which are in the entries being exported, (these entries should only be in in system as student has finalised
    the log book, so all entries exported are within these logbooks) then set the value of exported to True, so it is known
    how many un-exported log entries remain.
    """
    exportedBooks = LogBook.objects.filter(id__in=entries.values('book')).distinct()

    for book in exportedBooks:
        if book.exported == False:
            book.exported = True
            book.save()

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

            fields = ['book__user__user__username','book__user__user__first_name','book__user__user__last_name','year','book__category__name','book__organisation__code','book__organisation__name'] 
            entries=[]
            
            if not user == None and not organisation == None:
                entries = LogEntry.objects.filter(book__finalised=True,supervisor__validated=True,book__active=True,
                    status='Approved',book__organisation__exact = organisation,book__user = user
                    ).extra(select={'year': "EXTRACT(year FROM start)"}
                    ).values(*fields
                    ).annotate(startDate=Min('start'), endDate=Max('end'))
            elif not user == None:
                entries = LogEntry.objects.filter(book__finalised=True,supervisor__validated=True,book__active=True,
                    status='Approved',book__user = user
                    ).extra(select={'year': "EXTRACT(year FROM start)"}
                    ).values(*fields
                    ).annotate(startDate=Min('start'), endDate=Max('end'))
            elif not organisation == None:
                entries = LogEntry.objects.filter(book__finalised=True,supervisor__validated=True,book__active=True,
                    status='Approved',book__organisation = organisation
                    ).extra(select={'year': "EXTRACT(year FROM start)"}
                    ).values(*fields
                    ).annotate(startDate=Min('start'), endDate=Max('end'))
            else:
                """"
                Export ALL THE DATAS
                """
                out = io.BytesIO()
                orgs = Organisation.objects.all()
                entries = {}
                bufferedIO = []
                for org in orgs:
                    entries = LogEntry.objects.filter(book__finalised=True,supervisor__validated=True,book__active=True,
                    status='Approved',book__organisation = org
                    ).extra(select={'year': "EXTRACT(year FROM start)"}
                    ).values(*fields
                    ).annotate(startDate=Min('start'), endDate=Max('end'))

                    #initialise writer object
                    writer = None
                    if len(entries) > 0:
                        buffer = io.StringIO()
                        writer = csv.writer(buffer)
                        writer.writerow(['StudentID','First Name','Surname','Calendar Year','Position Type','Host Organisation','Host Organisation Code','Start Date','End Date','Hours'])
                        
                        for entry in entries:
                            writer.writerow([entry[f] for f in fields] + [entry['startDate'].strftime(DATE_FORMAT),entry['endDate'].strftime(DATE_FORMAT),round((entry['endDate']-entry['startDate']).seconds/3600)])

                        buffer.seek(0)
                        file_dict = {'file':buffer,'filename':org.name}
                        bufferedIO.append(file_dict)
                        
                    setExported(entries)
                    

                zipf = zipfile.ZipFile(out, mode='w')
                for b in bufferedIO:
                    zipf.writestr("{}.csv".format(b['filename']), b['file'].read())
                        
                zipf.close()
                out.seek(0)
                response = HttpResponse(out.read())
                response['Content-Disposition'] = 'attachment; filename=All Organisations.zip'
                
                return response

            setExported(entries)
            
            for entry in entries:
                writer.writerow([entry[f] for f in fields]
                        + [ entry['startDate'].strftime(DATE_FORMAT), entry['endDate'].strftime(DATE_FORMAT), round((entry['endDate']-entry['startDate']).seconds/3600)])
            return response

    else:
        form = ExportForm()
        
    context = dict(admin.site.each_context(request),
        form=form,)
    context['unexported_entries'] = getNumUnexported()
    return render(request, 'admin/logbook/export.html', context)
