from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import *

def indexView(request):
    return render(request, 'index.html', {})

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
    return redirect('index')
