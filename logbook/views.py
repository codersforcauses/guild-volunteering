from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import *

def index(request):

    return render(request, 'index.html', {})

def login(request):

    return render(request, 'login.html', {})

@login_required
def logout(request):

    return render(request, 'logout.html', {})
