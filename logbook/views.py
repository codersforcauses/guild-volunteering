# Database
from django.db import transaction
from django.db.models import ExpressionWrapper, F, Count, Sum, fields, Q

# User authentication
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

#Redirect
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django.urls import reverse

#Logbook Project
from .forms import *
from .admin import *
from django.conf import settings

#General
from django.template import RequestContext
from django.utils.crypto import get_random_string
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
import datetime
import hashlib
import json
import string


#Checks to see if the user passed to the function is a supervisor.
def is_supervisor(user):
    return user.groups.filter(name='LBSupervisor').exists()

#Checks to see if the user passed to the function is a student.
def is_lbuser(user):
    return user.groups.filter(name='LBStudent').exists()

#Creates headers which can be sorted for the tables in log books and log entries.
def makeHeaders(unformattedHeaderNames, currentOrder):
    '''
    Makes the headers and ordering urls for a list of models
    '''
    headerNames = [string.capwords(s.replace('_', ' ')) for s in unformattedHeaderNames]
    headerOrders = []
    # work out the urls for sorting when clinking on headers
    for i in range(1, len(headerNames)+1):
        newOrder = []
        # toggle between ascending and descending
        newOrder.append('-'+str(i) if str(i) in currentOrder else str(i))
        for n in currentOrder:
        # if previously sorted by this header don't include it twice
            if not str(i) in n:
                newOrder.append(n)
        headerOrders.append('.'.join(newOrder))
    return zip(headerNames, headerOrders)

def orderModels(order, unformattedHeaderNames, models):
    '''
    Orders models for a list of models
    '''
    if order == models:
        return
    sortArgs = []
    for i in order:
        if i[0] == '-':
            sortArgs.append('-'+unformattedHeaderNames[int(i[1])-1])
        else:
            sortArgs.append(unformattedHeaderNames[int(i[0])-1])
    return models.order_by(*sortArgs)

#Controls the actions when a user submits a POST on a form containing a number
# of elements in a table.
def modelActions(request, model, permissionCheck):
    action = request.POST['selectedAction']
    modelIDs = request.POST.getlist('model_selected')
    #Delete log book/s or entry/s
    if action == 'delete':
        for i in modelIDs:
            try:
                m = model.objects.get(id=i)
            except model.DoesNotExist:
                pass
            # ensure user has permission
            if permissionCheck(request.user, m, 'delete'):
                m.delete()
    #Submit log book/entries to be approved
    if action == 'submit':
        for i in modelIDs:
            try:
                m = model.objects.get(id=i)
            except model.DoesNotExist:
                pass
            if permissionCheck(request.user, m, 'submit'):
                try:
                    if m.status == 'Unapproved':
                        m.status = 'Pending'
                        m.save()
                # Then it is a logbook (surely a 'safer' way to do this?)
                except:
                    logentries = LogEntry.objects.filter(book=m.id)
                    for log in logentries:
                        if log.status == 'Unapproved':
                            log.status = 'Pending'
                            log.save()
    #Finalise Log Book/s
    if action == 'finalise':
        for i in modelIDs:
            try:
                m = model.objects.get(id=i)
            except model.DoesNotExist:
                pass
            
            if permissionCheck(request.user, m, 'finalise'):
                m.finalised = True
                m.save()
                    
    #Supervisor approve log entry
    if action == 'approve':
        for i in modelIDs:
            try:
                m = model.objects.get(id=i)
            except model.DoesNotExist:
                pass
            if permissionCheck(request.user, m, 'approve'):
                if m.status == 'Pending':
                    m.status = 'Approved'
                    m.save()
    #Supervisor decline log entry
    if action == 'decline':
        for i in modelIDs:
            try:
                m = model.objects.get(id=i)
            except model.DoesNotExist:
                pass
            if permissionCheck(request.user, m, 'decline'):
                if m.status == 'Pending':
                    m.status = 'Unapproved'
                    m.save()

"""
Below are checks to ensure the log book or the log entry can be interacted with
in the selected selected way by the user, if not it will return False.
"""
def logbookPermissionCheck(user, logbook, action):
    user = LBUser.objects.get(user=user)
    if action == 'delete':
        # Don't delete the book if it contains approved or pending entries
        entries = LogEntry.objects.filter(book=logbook, status__in=['Approved','Pending'])
        if len(entries) == 0:
            return True
    elif action == 'finalise':
        if hasAllApproved(logbook) == True:
            return True
        else:
            return False
    elif action == 'edit':
        if logbook.finalised == True or logbook.active == False:
            return False
        else:
            return True
    return user == logbook.user

def logentryPermissionCheck(user, logentry, action):
    if logentry.book.finalised == True:
        return False
    else:
        user = LBUser.objects.get(user=user)
        if user == logentry.book.user:
            if action == 'delete':
                # don't delete an approved entry
                if not logentry.status == 'Approved':
                    return True
        
            elif action == 'submit':
                return True

            elif action == 'edit':
                if not logentry.status == 'Approved':
                    return True
                else: return False
                
            return False
    
"""
A specific check for supervisors
"""
def approvePermissionCheck(user, logentry, action):
    user = Supervisor.objects.get(user=user)
    #limit actions to only allowed ones.
    if action == 'approve':
        return True
    if action == 'decline':
        return True
    return False
        
"""
Loads the 'front page' only if a user currently has an active session, otherwise
redirects to the login page.
"""
def indexView(request):
    if not request.user.is_authenticated():
        return redirect('logbook:login')
    #Checks if a user is a supervisor
    elif is_supervisor(request.user):
        is_super = True
        return render(request, 'index.html', {'is_super':is_super})
    #Checks to see if user is a student.
    elif is_lbuser(request.user):
        is_super = False
        return render(request, 'index.html', {'is_super':is_super})
    #If the user has not been assigned a user group this will show an error,
    #and tell user to talk to guild volunteering to check account settings.
    else:
        return render(request, 'error.html', {})

"""
Simple view to show the Frequently Asked Questions page
"""
def faqView(request):
    return render(request, 'faq.html', {})

#Function which checks to see if a specific logbook has all its logentries approved,
#this is a function which is ready to be finalised by the user.
def hasAllApproved(logbook):
    entries = LogEntry.objects.filter(book = logbook.id)
    if len(entries) == 0:
        return False
    for entry in entries:
        if entry.status == 'Unapproved' or entry.status == 'Pending':
            return False
    return True

@login_required
def loadBookView(request):
    if request.is_ajax():
        if request.method == "GET":
            
            book_id = request.GET['book_id']
            logbook = LogBook.objects.get(id=book_id)
            #object
            output = {'name':logbook.name,'category':logbook.category.name}
            #response
            output = json.dumps(output, cls=DjangoJSONEncoder)
            return HttpResponse(output, content_type='application/json')
        
        else:
            return HttpResponseForbidden()
        
    else:
        return HttpResponseForbidden()

@login_required
def editLogBookView(request):
    if request.method == "POST":
        edit_form = EditLogBookForm(request.POST)
        
        if edit_form.is_valid():
            name_form = edit_form.cleaned_data['name']
            category_form = edit_form.cleaned_data['category']
            
            book_id = request.POST['book_id']
            logbook = LogBook.objects.get(id=book_id)

            if logbookPermissionCheck(request.user, logbook, 'edit'):
                logbook.name = name_form
                logbook.category = category_form

                logbook.save()
                return redirect('logbook:list')
            else:
                return redirect('logbook:list')
        else:
            return HttpResponseForbidden()
            
    else:
        return HttpResponseForbidden()

"""
View which handles the request from a user to add a logbook.
"""
@login_required
def addLogBookView(request):
    if request.method == "POST":
        form = LogBookForm(request.POST)
        if form.is_valid():
            logbook = LogBook.objects.create(name=form.cleaned_data['bookName'],
                                             organisation=form.cleaned_data['bookOrganisation'],
                                             category=form.cleaned_data['bookCategory'],
                                             user=LBUser.objects.get(user=request.user))
            logbook.save()
            return redirect('logbook:list')
    else:
        form = LogBookForm()
    return render(request, 'form.html', {'title':'Create Logbook',
                                         'form':form,
                                         'backUrl':reverse('logbook:list')})
@login_required
def updateHoursList(request):
    if request.is_ajax():
        if request.method == "POST":
            modelActions(request, LogEntry, approvePermissionCheck)
            logbook = request.POST['book_id']
            data = {'entries':len(LogEntry.objects.filter(book = logbook, status='Pending')),
                    'checkboxid':request.POST['model_selected'], 'book':request.POST['book_id']}
                
            return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponseForbidden()

"""
View used as the main page to do with the logbook system for both supervisors
and students

Supervisors: They see all the logentries which are requiring approval and
those which they have approved.

Students: See the list of logbooks they have created with different orgs,
can edit these books to change fields e.g. the category of the volunteering.
Allows them to finalise books as well as see past books
"""
@login_required
def booksView(request):
    #Supervisor
    if is_supervisor(request.user):
        if request.method == 'POST':
            modelActions(request, LogEntry, approvePermissionCheck)
            
        entries = LogEntry.objects.filter(supervisor__user = request.user, status='Pending')\
              .values('book__user__user__username','book__user__user__first_name','book__user__user__last_name','book__id')\
              .annotate(entries_pending=Count('id'))\
              .annotate(entries_pending_total_duration=Sum(ExpressionWrapper(F('end') - F('start'), output_field=fields.DurationField())))
        #use books to get the student numbers
        logentries = LogEntry.objects.filter(supervisor__user = request.user, status='Pending')
        return render(request, 'supervisor.html', {'logbooks':entries,
                                                   'entries':logentries})
    #Student
    elif is_lbuser(request.user):
        if request.method == 'POST':
            add_form = LogBookForm(request.POST)
            if add_form.is_valid():
                org = add_form.cleaned_data['bookOrganisation']
                #Restricts user to only 1 active logbook per organisation
                if len(LogBook.objects.filter(user__user=request.user, active = True, organisation = org)) == 0:
                    logbook = LogBook.objects.create(name=add_form.cleaned_data['bookName'],
                                                 organisation=add_form.cleaned_data['bookOrganisation'],
                                                 category=add_form.cleaned_data['bookCategory'],
                                                 user=LBUser.objects.get(user=request.user))
                    logbook.save()
                    return redirect('logbook:list')
                else:
                    return redirect('logbook:list')
            else:
                modelActions(request, LogBook, logbookPermissionCheck)
                
        add_form = LogBookForm()
        edit_form = EditLogBookForm()
        
        # display page
        currentOrder = request.GET.get('order', [])
        if currentOrder:
            currentOrder = currentOrder.split('.')
        unformattedHeaderNames = LogBookAdmin.list_display[1:4] # leave out the student
        headers = makeHeaders(unformattedHeaderNames, currentOrder)
        
        logbooks = LogBook.objects.filter(user__user=request.user, active = True)
        logbooks = orderModels(currentOrder, unformattedHeaderNames, logbooks)
        logbooks_list = list(logbooks)
        approvedLogbooks = list()

        finalisedbooks = LogBook.objects.filter(user__user=request.user, active = True, finalised = True)
        pastbooks = LogBook.objects.filter(user__user=request.user,active=False, finalised=True)        
        for book in logbooks:
            if hasAllApproved(book):
                approvedLogbooks.append(book)
                logbooks_list.remove(book)
                
        isFinalisable = False
        if len(approvedLogbooks) > 0:
            isFinalisable = True
            
        return render(request, 'books.html', {'logbooks':logbooks_list,
                                              'approvedbooks':approvedLogbooks,
                                              'headers':headers,
                                              'form':add_form,'edit_form':edit_form,
                                              'isFinalisable':isFinalisable,
                                              'pastbooks':pastbooks,
                                              'finalisedbooks':finalisedbooks})
    else:
        return render(request, 'error.html', {})

"""
View to handle the create temp supervisor form when it is submitted in log entry
"""
@login_required
def createTempSupervisorView(request, pk):
    logbook = LogBook.objects.get(id=pk)
    org = logbook.organisation
    
    if request.method == 'POST':
        
        form = TempSupervisorForm(request.POST)
        if form.is_valid():
            
            data = {}
            data['supervisor_email'] = form.cleaned_data['email']
            data['organisation'] = org
            data['email_path']="email_templatesTempSupervisor.txt"
            data['email_subject']="Verify Supervisor Account"

            form.sendMail(data)
            form.save(data) #Save the Supervisor model NO user in the system YET!.
            return redirect(reverse('logbook:view', args=[logbook.id]))
        else:
            return redirect(reverse('logbook:view', args=[logbook.id]))
    else:
        return redirect(reverse('logbook:view', args=[logbook.id]))

@login_required
def loadEntryView(request):
    if request.is_ajax():
        if request.method == "GET":
            entry_id = request.GET['entry']
            logentry = LogEntry.objects.get(id=entry_id)
            output = {'name':logentry.name, 'supervisor':logentry.supervisor.email,'start':logentry.start, 'end':logentry.end}
            output = json.dumps(output, cls=DjangoJSONEncoder)
            print(output)
            return HttpResponse(output, content_type='application/json')
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

"""
View which handles the request from a user to add a logbook.
"""
@login_required
def editLogEntryView(request, pk):
    logbook = LogBook.objects.get(id=pk)
    org = logbook.organisation
    if request.method == "POST":
        logentry_id = request.POST['entry_id']
        if logentry_id == None:
            return HttpResponseForbidden()
        entry = LogEntry.objects.get(id=logentry_id)
        editEntryForm = EditLogEntryForm(request.POST, org_id = org.id)

        if editEntryForm.is_valid():
            
            if logentryPermissionCheck(request.user, entry, 'edit'):
                entry.name = editEntryForm.cleaned_data['name']
                entry.supervisor = editEntryForm.cleaned_data['supervisor']
                entry.start = editEntryForm.cleaned_data['start']
                entry.end = editEntryForm.cleaned_data['end']
                entry.save()
                
                return redirect(reverse('logbook:view', args=[logbook.id]))
            else:
                return HttpResponseForbidden()
        else:
            return redirect(reverse('logbook:view', args=[logbook.id]))
    else:
        return redirect(reverse('logbook:view', args=[logbook.id]))


"""
View to handle the request to add a log entry.
"""
@login_required
def addLogEntryView(request, pk):
    logbook = LogBook.objects.get(id=pk)
    org = logbook.organisation
    if request.method == 'POST':
        addEntryForm = LogEntryForm(request.POST, org_id = org.id)
        if addEntryForm.is_valid():
            logentry = LogEntry.objects.create(name=addEntryForm.cleaned_data['name'],
                                               supervisor=addEntryForm.cleaned_data['supervisor'],
                                               start=addEntryForm.cleaned_data['start'],
                                               end=addEntryForm.cleaned_data['end'],
                                               book=logbook)
            logentry.save()
            return redirect(reverse('logbook:view', args=[logbook.id]))

        return redirect(reverse('logbook:view', args=[logbook.id]))

"""
Shows the student the list of log entries they have which are part of this logbook
Allows the user to add,delete and submit log entries through this page.
"""
@login_required
def logEntryView(request, pk):
    logbook = LogBook.objects.get(id=pk)
    org = logbook.organisation
    if logbook == None or logbook.active == False:
        return HttpResponseForbidden()

    # check that user is accessing their own book
    if logbook.user != request.user.lbuser:
         return HttpResponseForbidden()

    if request.method == 'POST':
        modelActions(request, LogEntry, logentryPermissionCheck)

    addEntryForm = LogEntryForm(org_id = org.id)
    editEntryForm = EditLogEntryForm(org_id = org.id)
    tempSupervisorForm = TempSupervisorForm()
    
    logentries = {}
    logbooks = {}
    try:
        #Get all the logbooks this user 'owns'
        logbooks = LogBook.objects.filter(user__user=request.user)
        #Get all the log entries for this logbook
        logentries = LogEntry.objects.filter(book=logbook)
    except LogEntry.DoesNotExist:
        pass

    unapproved_entries = False
    for entry in logentries:
        if entry.status == "Unapproved":
            unapproved_entries = True
            break
    
    currentOrder = request.GET.get('order', [])
    #Orders the outputted table based on the sorting of headings user has selected.
    if currentOrder:
        currentOrder = currentOrder.split('.')
        
    unformattedHeaderNames = LogEntryAdmin.list_display[1:5] # leave out book name and creation/update times
    headers = makeHeaders(unformattedHeaderNames, currentOrder)
    logentries = orderModels(currentOrder, unformattedHeaderNames, logentries)

    return render(request, 'logentry.html', {'entries':logentries,
                                             'unapproved_entries':unapproved_entries,
                                             'logbooks':logbooks,
                                             'book':logbook,
                                             'headers':headers,
                                             'addentry_form':addEntryForm,
                                             'edit_form':editEntryForm,
                                             'createsuper_form':tempSupervisorForm})

"""
Manages the logging in of a user via django.auth functions.
"""
def loginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('logbook:index')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'loginForm':form})

"""
Function to safely generate an activation key allowing the user verify their account.
"""
def generate_activation_key(username):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(20, chars)
    return hashlib.sha256((secret_key + username).encode('utf-8')).hexdigest()

"""
Sign-up view creates a user from the entered SignUpForm and then sends the user
an email using a generated key to ensure the user has secure access to the said
email account.
"""
@transaction.atomic
def signupView(request):
    if request.user.is_authenticated():
        return redirect('logbook:index')
    '''
    View for handling student registration
    '''
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            data = {}
            data['username'] = form.cleaned_data['username']
            data['email'] = form.cleaned_data['username'] + '@student.uwa.edu.au'
            data['first_name'] = form.cleaned_data['first_name']
            data['last_name'] = form.cleaned_data['last_name']
            data['password'] = form.cleaned_data['password']
            data['activation_key'] = generate_activation_key(data['username'])
            
            data['email_path']="email_templates/ActivationEmail.txt"
            data['email_subject']="Activate your Guild Volunteering account"

            form.sendVerifyEmail(data)
            form.save(data) #Save the user and lbuser

            request.session['registered']=True #For display purposes
            return redirect('logbook:login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'signupForm':form})

"""
View which simply checks to see if the activation code the user has used, is
a valid code, if not then the page will tell the user it is not a valid code.
If the code has been user after the activation period then the user will need
to request a new activation link
"""
def activation(request, key):
    activation_expired = False
    already_active = False
    id_user = None
    lbuser = get_object_or_404(LBUser, activation_key=key)
    if lbuser.user.is_active == False:
        if timezone.now() > lbuser.key_expires:
            #Display: offer the user to send a new activation link
            activation_expired = True 
            id_user = lbuser.user.id
        else:
            #Activation successful
            lbuser.user.is_active = True
            lbuser.user.save()

    #If user is already active, simply display error message
    else:
        #Display : error message
        already_active = True
    return render(request, 'activation.html', {'activation_expired':activation_expired,'isActive':already_active,'user_id':id_user})

"""
Function used to send users a new acivation code in the instance that their
activation code expires, see the main program settings under DAYS_VALID,
it may be altered depending on what situation admin wants.
"""
def new_activation_link(request, user_id):
    form = SignupForm()
    datas={}
    user = User.objects.get(id=user_id)
    if user is not None and not user.is_active:
        datas['username']=user.username
        datas['email']=user.email
        datas['email_path']="email_templates/NewActivationEmail.txt"
        datas['email_subject']="New Activation Link"
        datas['first_name'] = user.first_name
        datas['activation_key']= generate_activation_key(datas['username'])

        lbuser = LBUser.objects.get(user=user)
        lbuser.activation_key = datas['activation_key']
        lbuser.key_expires = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=settings.DAYS_VALID), "%Y-%m-%d %H:%M:%S")
        lbuser.save()

        form.sendVerifyEmail(datas)
        request.session['new_link']=True #Display: new link sent

    return redirect('logbook:login')

@transaction.atomic
def supervisorSignupView(request):
    '''
    View for handling supervisor registraion
    Uses the same template as signupView, but with a different form
    '''
    if request.method == 'POST':
        form = SupervisorSignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'],
                                            form.cleaned_data['username'],
                                            form.cleaned_data['password'])
            user.save()
            group = Group.objects.get(name='LBSupervisor')
            group.user_set.add(user)
            group.save()
            return redirect('logbook:login')
    else:
        form = SupervisorSignupForm()
    return render(request, 'signup.html', {'signupForm':form})

#Simple view that ends the user's session.
@login_required
def logoutView(request):
    logout(request)
    return redirect('logbook:login')

#Function which uses the deleteForm to simply suspend a user's account, by making it inactive.
@login_required
def deleteUserView(request):
    user = request.user
    if request.method == 'POST':
        deleteForm = DeleteUserForm(request.POST, instance=user)
        if deleteForm.is_valid():
            active = deleteForm.save()
            #Logout User
            return redirect('logbook:login')
    else:
        return redirect('logbook:profile')

"""
View to handle when a user sends a POST on a form to edit their first and last names.
"""
@login_required
def editNamesView(request):
    user = request.user
    if request.method == 'POST':
        editNamesForm = EditNamesForm(request.POST)
        if editNamesForm.is_valid():
            user.first_name = editNamesForm.cleaned_data['first_name']
            user.last_name = editNamesForm.cleaned_data['last_name']
            user.save()
            return redirect('logbook:profile')
    else:
        return redirect('logbook:profile')

"""
View which simply gives the user some functions to do with their account
e.g. Suspend account, change password (not have to reset password), and change names
"""
@login_required
def profileView(request):
    # Staff member can view analytics in profile or in index
    if request.user.is_staff:
        print('Staff User')
    user = request.user
    if request.method == 'POST':
        changePasswordForm = PasswordChangeForm(request.user, request.POST)
        if changePasswordForm.is_valid():
            user = changePasswordForm.save()
            update_session_auth_hash(request, user)
            request.method = 'GET'
        return redirect('logbook:profile')
    else:
        editNamesForm = EditNamesForm(instance=request.user)
        changePasswordForm = PasswordChangeForm(request.user)
        deleteForm = DeleteUserForm(instance=user)

    return render(request, 'profile.html', {'names_form':editNamesForm,
                                            'delete_form':deleteForm,
                                            'change_password_form':changePasswordForm}
                  )

"""
View used to query the Guild Volunteering site, but also supplies context if 'get' used
"""
def searchBarView(request):
    if request.method == 'POST':
        
        search_form = SearchBarForm(request.POST)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['query']
            search_url = "http://websiteindevelopment.biz/wordpress/volunteering/?s="+search_query
            return redirect(search_url)

        else:
            return HttpResponseNotFound
    else:
        return HttpResponseNotFound
