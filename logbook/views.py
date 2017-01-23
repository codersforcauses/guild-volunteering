from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import *

def is_supervisor(user):
    try:
        user.supervisor.validated
        return True
    except:
        return False

def indexView(request):

    # If we use a decorator, it doesn't redirect at all.
    if not request.user.is_authenticated():
        return redirect('login')
    else:
        if is_supervisor(request.user):
            logentries = LogEntry.objects.filter(supervisor__user = request.user)
            return render(request, 'super_index.html', {'logentries':logentries})
        else:
            logbooks = LogBook.objects.filter(user__user = request.user)
            return render(request, 'index.html', {'logbooks':logbooks})

@login_required
def logentryView(request, username, logbook_id):

    logentries = {}
    logbook = {}
    logbooks = {}
    
    try:
        logbooks = LogBook.objects.filter(user__user = request.user)
        logbook = logbooks.get(id = logbook_id)
        logentries = LogEntry.objects.filter(book = logbook_id)

    except LogEntry.DoesNotExist:
        pass

    return render(request, 'logentry.html', {'entries':logentries,
                                             'logbooks':logbooks,'book':logbook})

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
