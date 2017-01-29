from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import *
from .admin import *

import string


# For testing until merged with proper supervisor code
def is_supervisor(user):
        return False

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

def logbookPermissionCheck(user, logbook, action):
    user = LBUser.objects.get(user=user)
    return user == logbook.user

def logentryPermissionCheck(user, logentry, action):
    user = LBUser.objects.get(user=user)
    return user == logentry.book.user


def indexView(request):
    # If we use a decorator, it doesn't redirect at all.
    if not request.user.is_authenticated():
        return redirect('login')
    else:
        if is_supervisor(request.user):
            logentries = LogEntry.objects.filter(supervisor__user = request.user)
            return render(request, 'super_index.html', {'logentries':logentries})
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
            return render(request, 'index.html', {'logbooks':logbooks, 'headers':headers})



@login_required
def logentryView(request, username, logbook_name_slug):
    # check that user is accessing their own book
    if username != request.user.username:
         return HttpResponseForbidden()

    if request.method == 'POST':
        modelActions(request, LogEntry, logentryPermissionCheck)

    logentries = {}
    logbook = {}
    logbooks = {}
    try:
        logbooks = LogBook.objects.filter(user__user=request.user)
        logbook = logbooks.get(name_slug=logbook_name_slug)
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
            user = authenticate(username=form.cleaned_data['studentNum'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = LoginForm()
    # If data did not validate will re-render the page with the same form
    # Form now has an error message
    return render(request, 'login.html', {'loginForm':form})

def signupView(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['studentNum'],
                                            form.cleaned_data['studentNum'] + '@student.uwa.edu.au',
                                            form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'signupForm':form})
    

@login_required
def logoutView(request):
    logout(request)
    return redirect('login')

@login_required
def profileView(request):

    # Staff member can view analytics in profile or in index
    if request.user.is_staff:
        print('Staff User')

    return render(request, 'profile.html', {})
