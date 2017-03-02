from django.shortcuts import render, redirect

# Database
from .forms import *
from django.db import transaction
from django.db.models import ExpressionWrapper, F, Count, Sum, fields

# User authentication
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm

#Redirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import get_object_or_404

#Logbook Project
from .forms import *
from .admin import *
from django.conf import settings

#General
from django.utils.crypto import get_random_string
import hashlib
import string
import datetime
from django.utils import timezone

def is_supervisor(user):
    return user.groups.filter(name='LBSupervisor').exists()

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

def modelActions(request, model, permissionCheck):
    action = request.POST['selectedAction']
    modelIDs = request.POST.getlist('model_selected')
    if action == 'delete':
        for i in modelIDs:
            try:
                m = model.objects.get(id=i)
            except model.DoesNotExist:
                pass
            # ensure user has permission
            if permissionCheck(request.user, m, 'delete'):
                m.delete()

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
    if action == 'edit':
        for i in modelIDs:
            try:
                m = model.objects.get(id=i)
            except model.DoesNotExist:
                pass
            if permissionCheck(request.user, m, 'edit'):
                try:
                    print('yes')
                    logentry = LogEntry.objects.get(id=m.id)
                    print(logentry.book.id,logentry.id)
                    return redirect('edit_entry',args=(logentry.book.id, logentry.id))
                except:
                    print('rip')
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


def logbookPermissionCheck(user, logbook, action):
    user = LBUser.objects.get(user=user)
    if action == 'delete':
        # Don't delete the book if it contains approved entries
        entries = LogEntry.objects.filter(book=logbook, status=LogEntry.APPROVED)
        if len(entries) > 0:
            return False
    return user == logbook.user

def logentryPermissionCheck(user, logentry, action):
    if action == 'delete':
        # don't delete an approved entry
        if logentry.status == LogEntry.APPROVED:
            return False
    user = LBUser.objects.get(user=user)
    return user == logentry.book.user

def approvePermissionCheck(user, logentry, action):
    user = Supervisor.objects.get(user=user)
    #limit actions to only allowed ones.
    if action == 'approve':
        return True
    if action == 'decline':
        return True
    return False
        

def indexView(request):
    if not request.user.is_authenticated():
        return redirect('logbook:login')
    else:
        is_super = is_supervisor(request.user)
        return render(request, 'index.html', {'is_super':is_super})

def faqView(request):

    return render(request, 'faq.html', {})

def hasAllApproved(logbook):
    entries = LogEntry.objects.filter(book = logbook.id)
    if len(entries) == 0:
        return False
    for entry in entries:
        if entry.status == 'Unapproved' or entry.status == 'Pending':
            return False
    return True


@login_required
def booksView(request):
    if is_supervisor(request.user):
        if request.method == 'POST':
            modelActions(request, LogEntry, approvePermissionCheck)
        entries = LogEntry.objects.filter(supervisor__user = request.user, status='Pending')\
              .values('book__user__user__username','book__user__user__first_name','book__user__user__last_name','book__id')\
              .annotate(entries_pending=Count('id'))\
              .annotate(entries_pending_total_duration=Sum(ExpressionWrapper(F('end') - F('start'), output_field=fields.DurationField())))
        #use books to get the student numbers
        logentries = LogEntry.objects.filter(supervisor__user = request.user, status='Pending')
        return render(request, 'supervisor.html', {'logbooks':entries,'entries':logentries})
    else:
        if request.method == 'POST':
            add_form = LogBookForm(request.POST)
            if add_form.is_valid():
                logbook = LogBook.objects.create(name=add_form.cleaned_data['bookName'],
                                             description=add_form.cleaned_data['bookDescription'],
                                             organisation=add_form.cleaned_data['bookOrganisation'],
                                             category=add_form.cleaned_data['bookCategory'],
                                             user=LBUser.objects.get(user=request.user))
                logbook.save()
                return redirect('logbook:list')
            else:
                modelActions(request, LogBook, logbookPermissionCheck)
        add_form = LogBookForm()
        # display page
        currentOrder = request.GET.get('order', [])
        if currentOrder:
            currentOrder = currentOrder.split('.')
        unformattedHeaderNames = LogBookAdmin.list_display[1:5] # leave out the sutdent
        headers = makeHeaders(unformattedHeaderNames, currentOrder)
        logbooks = LogBook.objects.filter(user__user=request.user)
        logbooks = orderModels(currentOrder, unformattedHeaderNames, logbooks)
        logbooks_list = list(logbooks)
        approvedLogbooks = list()
        for book in logbooks:
            if hasAllApproved(book):
                approvedLogbooks.append(book)
                logbooks_list.remove(book)
                
        return render(request, 'books.html', {'logbooks':logbooks_list,'approvedbooks':approvedLogbooks, 'headers':headers,'form':add_form})

@login_required
def logentryView(request, pk):
    logbook = LogBook.objects.get(id=pk)
    org = logbook.organisation
    if logbook == None:
        return HttpResponseNotFound

    # check that user is accessing their own book
    if logbook.user != request.user.lbuser:
         return HttpResponseForbidden()

    if request.method == 'POST':

        addEntryForm = LogEntryForm(request.POST, org_id = org.id)
        if addEntryForm.is_valid():
            logentry = LogEntry.objects.create(description=addEntryForm.cleaned_data['description'],
                                               supervisor=addEntryForm.cleaned_data['supervisor'],
                                               start=addEntryForm.cleaned_data['start'],
                                               end=addEntryForm.cleaned_data['end'],
                                               book=logbook)
            logentry.save()
            return redirect(reverse('logbook:view', args=[logbook.id]))

        else:
            try:
                modelActions(request, LogEntry, logentryPermissionCheck)
            except:
                pass

    addEntryForm = LogEntryForm(org_id = org.id)

    logentries = {}
    logbooks = {}
    try:
        logbooks = LogBook.objects.filter(user__user=request.user)
        logentries = LogEntry.objects.filter(book=logbook)
    except LogEntry.DoesNotExist:
        pass

    currentOrder = request.GET.get('order', [])
    if currentOrder:
        currentOrder = currentOrder.split('.')
    unformattedHeaderNames = LogEntryAdmin.list_display[1:5] # leave out book name and creation/update times
    headers = makeHeaders(unformattedHeaderNames, currentOrder)
    logentries = orderModels(currentOrder, unformattedHeaderNames, logentries)

    return render(request, 'logentry.html', {'entries':logentries,
                                             'logbooks':logbooks,
                                             'book':logbook,
                                             'headers':headers,
                                             'addentry_form':addEntryForm,})

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

def generate_activation_key(username):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(20, chars)
    return hashlib.sha256((secret_key + username).encode('utf-8')).hexdigest()

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
            
            data['email_path']="ActivationEmail.txt"
            data['email_subject']="Activate your Guild Volunteering account"

            form.sendVerifyEmail(data)
            form.save(data) #Save the user and lbuser

            request.session['registered']=True #For display purposes
            return redirect('logbook:login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'signupForm':form})

def activation(request, key):
    activation_expired = False
    already_active = False
    id_user = None
    lbuser = get_object_or_404(LBUser, activation_key=key)
    if lbuser.user.is_active == False:
        if timezone.now() > lbuser.key_expires:
            activation_expired = True #Display: offer the user to send a new activation link
            id_user = lbuser.user.id
        else: #Activation successful
            lbuser.user.is_active = True
            lbuser.user.save()

    #If user is already active, simply display error message
    else:
        already_active = True #Display : error message
    return render(request, 'activation.html', {'activation_expired':activation_expired,'isActive':already_active,'user_id':id_user})

def new_activation_link(request, user_id):
    form = SignupForm()
    datas={}
    user = User.objects.get(id=user_id)
    if user is not None and not user.is_active:
        datas['username']=user.username
        datas['email']=user.email
        datas['email_path']="NewActivationEmail.txt"
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



@login_required
def logoutView(request):
    logout(request)
    return redirect('logbook:login')

@login_required
def profileView(request):
    # Staff member can view analytics in profile or in index
    if request.user.is_staff:
        print('Staff User')
    user = request.user
    if request.method == 'POST':
        editNamesForm = EditNamesForm(request.POST)
        changePasswordForm = PasswordChangeForm(request.user, request.POST)
        deleteForm = DeleteUserForm(request.POST, instance=user)
        if editNamesForm.is_valid():
            user.first_name = editNamesForm.cleaned_data['first_name']
            user.last_name = editNamesForm.cleaned_data['last_name']
            user.save()
            return redirect('logbook:profile')
        elif changePasswordForm.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
        elif deleteForm.is_valid:
            active = deleteForm.save()
            #Logout User
            return redirect('logbook:login')
    else:
        editNamesForm = EditNamesForm(instance=user)
        changePasswordForm = PasswordChangeForm(request.user)
        deleteForm = DeleteUserForm(instance=user)

    return render(request, 'profile.html', {'names_form':editNamesForm,'delete_form':deleteForm,'change_password_form':changePasswordForm})

@login_required
def addLogbookView(request):
    if request.method == 'POST':
        form = LogBookForm(request.POST)
        if form.is_valid():
            logbook = LogBook.objects.create(name=form.cleaned_data['bookName'],
                                             description=form.cleaned_data['bookDescription'],
                                             organisation=form.cleaned_data['bookOrganisation'],
                                             category=form.cleaned_data['bookCategory'],
                                             user=LBUser.objects.get(user=request.user))
            logbook.save()
            return redirect('logbook:list')
    else:
        form = LogBookForm()
    return render(request, 'form.html', {'title':'Create Logbook', 'form':form, 'backUrl':reverse('logbook:list')})

@login_required
def addLogEntryView(request, pk):
    logbook = LogBook.objects.get(id=pk)
    if logbook == None:
        return HttpResponseNotFound

    # check that user is accessing their own book
    if logbook.user != request.user.lbuser:
         return HttpResponseForbidden()

    if request.method == 'POST':
        print('was post')
        form = LogEntryForm(request.POST)
        if form.is_valid():
            print('was valid')
            logentry = LogEntry.objects.create(description=form.cleaned_data['description'],
                                               supervisor=form.cleaned_data['supervisor'],
                                               start=form.cleaned_data['start'],
                                               end=form.cleaned_data['end'],
                                               book=logbook)
            logentry.save()
            print('redirecting')
            return redirect(reverse('logbook:view', args=[logbook.id]))
    else:
        form = LogEntryForm()
    return render(request, 'form.html', {'title':'Create Log Entry', 'form':form, 'backUrl':reverse('logbook:view', args=[logbook.id])})

@login_required
def editLogEntryView(request, pk, log_id):
    logbook = LogBook.objects.get(id=pk)
    logentry = LogEntry.objects.get(id = log_id)
    if logentry == None:
        return HttpResponseNotFound

    if logbook.user != request.user.lbuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        editForm = LogEntryForm(request.POST)
        if editForm.valid():
            LogEntry.objects.get(id=log_id).update(description=form.cleaned_data['description'],
                                               supervisor=form.cleaned_data['supervisor'],
                                               start=form.cleaned_data['start'],
                                               end=form.cleaned_data['end'],
                                               updated_at=datetime.datetime.now())

    else:
        editForm = LogEntryForm()

    return render(request, 'form.html', {'title':'Edit Log Entry', 'form':editForm,'book':logbook, 'backUrl':reverse('logbook:view', args=[logbook.id])})
