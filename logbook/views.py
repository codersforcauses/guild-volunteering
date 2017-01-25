from django.shortcuts import render, redirect

# Database
from .forms import *
from django.db import transaction
from django.db.models import F

# User authentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

def is_supervisor(user):
    return user.groups.filter(name='LBSupervisor').exists()

def indexView(request):
    # If we use a decorator, it doesn't redirect at all.
    if not request.user.is_authenticated():
        return redirect('login')
    else:
        if is_supervisor(request.user):
            entries = LogEntry.objects.filter(supervisor__user = request.user, status='Pending').values('book').distinct()
            #use books to get the student numbers
            logbooks = LogBook.objects.filter(id__in = entries)
            return render(request, 'super_index.html', {'logbooks':logbooks})
        else:
            logbooks = LogBook.objects.filter(user__user = request.user)
            return render(request, 'index.html', {'logbooks':logbooks})

def loginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('index')
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
            return redirect('login')
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
            return redirect('login')
    else:
        form = SupervisorSignupForm()
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
