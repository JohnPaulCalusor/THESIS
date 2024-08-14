from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

# Create your views here.

def index(request):
    return render(request, 'papsas_app/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        fname = request.POST['fName']
        lname = request.POST['lName']
        mobileNum = request.POST['mobileNum']
        region = request.POST['region']
        address = request.POST['address']
        occupation = request.POST['occupation']
        age = request.POST['age']
        memType = request.POST['memType']
        birthDate = request.POST['birthDate']
        
        user = User.objects.create_user(username = username,
                                        email= username, 
                                        password=password, 
                                        first_name=fname, 
                                        last_name= lname,
                                        mobileNum= mobileNum,
                                        region = region,
                                        address = address,
                                        occupation = occupation,
                                        age = age,
                                        memType = memType,
                                        birthdate = birthDate)
        user.save()
        login(request, user)
        return render(request, 'papsas_app/index.html', {
            'user' : request.user,
            'message' : 'Registered Successfully'
        })
    else:
        return render(request, 'papsas_app/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, 'papsas_app/login.html', {
                'message' : 'Invalid Credentials'
                })
    else:
        return render(request, 'papsas_app/login.html')
