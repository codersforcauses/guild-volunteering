from django.shortcuts import render, redirect

# Database
from .forms import *
from django.db import transaction
from django.db.models import F, Count, Sum

# User authentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from django.http import HttpResponseNotFound, HttpResponseForbidden

from django.urls import reverse

from .forms import *
from .admin import *

import string
import datetime

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
                    

def logbookPermissionCheck(user, logbook, action):
    user = LBUser.objects.get(user=user)
    return user == logbook.user

def logentryPermissionCheck(user, logentry, action):
    user = LBUser.objects.get(user=user)
    return user == logentry.book.user


def indexView(request):
    # If we use a decorator, it doesn't redirect at all.
    if not request.user.is_authenticated():
        return redirect('logbook:login')
    else:
        return render(request, 'index.html', {})

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
        entries = LogEntry.objects.filter(supervisor__user = request.user, status='Pending').values('book__user__user__username','book__user__user__first_name','book__user__user__last_name').annotate(entries_pending=Count('id'))
        #use books to get the student numbers
        #logbooks = LogBook.objects.filter(id__in = entries)
        ApprovalCount = LogEntry.objects.filter(supervisor__user = request.user, status='Pending').values('book').annotate(Count('id'))
        print(ApprovalCount)
        
        return render(request, 'supervisor.html', {'logbooks':entries,})
    else:
        if request.method == 'POST':
            modelActions(request, LogBook, logbookPermissionCheck)
        # display page
        currentOrder = request.GET.get('order', [])
        if currentOrder:
            currentOrder = currentOrder.split('.')
        unformattedHeaderNames = LogBookAdmin.list_display[1:] # leave out the sutdent
        headers = makeHeaders(unformattedHeaderNames, currentOrder)
        logbooks = LogBook.objects.filter(user__user=request.user)
        logbooks = orderModels(currentOrder, unformattedHeaderNames, logbooks)
        logbooks_list = list(logbooks)
        approvedLogbooks = list()
        for book in logbooks:
            if hasAllApproved(book):
                approvedLogbooks.append(book)
                logbooks_list.remove(book)
        print(approvedLogbooks)
        return render(request, 'books.html', {'logbooks':logbooks_list,'approvedbooks':approvedLogbooks, 'headers':headers})

@login_required
def logentryView(request, pk):
    logbook = LogBook.objects.get(id=pk)
    if logbook == None:
        return HttpResponseNotFound

    # check that user is accessing their own book
    if logbook.user != request.user.lbuser:
         return HttpResponseForbidden()

    if request.method == 'POST':
        modelActions(request, LogEntry, logentryPermissionCheck)

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
    unformattedHeaderNames = LogEntryAdmin.list_display[1:] # leave out book name and creation/update times
    headers = makeHeaders(unformattedHeaderNames, currentOrder)
    logentries = orderModels(currentOrder, unformattedHeaderNames, logentries)

    return render(request, 'logentry.html', {'entries':logentries,
                                             'logbooks':logbooks,
                                             'book':logbook,
                                             'headers':headers})

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

@transaction.atomic
def signupView(request):
    '''
    View for handling student registration
    '''
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'],
                                            form.cleaned_data['username'] + '@student.uwa.edu.au',
                                            form.cleaned_data['password'])
            user.save()
            group = Group.objects.get(name='LBStudent')
            group.user_set.add(user)
            group.save()
            return redirect('logbook:login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'signupForm':form})

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

    return render(request, 'profile.html', {})

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
    return render(request, 'form.html', {'title':'Create Logbook', 'form':form})

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
    return render(request, 'form.html', {'title':'Create Log Entry', 'form':form,'book':logbook})

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

    return render(request, 'form.html', {'title':'Edit Log Entry', 'form':editForm,'book':logbook})
