from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .models import User, Officer, Candidacy, Election, Event, Attendance, EventRegistration, MembershipTypes, UserMembership
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
from .forms import AttendanceForm, EventRegistrationForm, EventForm, ProfileForm, RegistrationForm, LoginForm, MembershipRegistration
from datetime import date


# Create your views here.

def index(request):
    today = date.today()
    events = Event.objects.all()
    upcoming_events = [event for event in events if event.startDate > today]
    return render(request, 'papsas_app/index.html', {
        'events' : upcoming_events,
    })

def register(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            fname = form.cleaned_data['first_name']
            lname = form.cleaned_data['last_name']
            mobileNum = form.cleaned_data['mobileNum']
            region = form.cleaned_data['region']
            address = form.cleaned_data['address']
            occupation = form.cleaned_data['occupation']
            age = form.cleaned_data['age']
            birthDate = form.cleaned_data['birthdate']

            if region == 'Region':
                return render(request, 'papsas_app/register.html', {
                'form': form,
                'message' : 'Please input a region'
            })          
            else:

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
                                            birthdate = birthDate)
                user.save()
                # Generate 6-digit verification code
                verification_code = random.randint(100000, 999999)

                # Save verification code to user's profile
                user.verification_code = verification_code
                user.save()

            # Send verification email
                subject = 'Verify your email address'
                message = f'Dear {user.first_name},\n\nYour verification code is: {verification_code}\n\nPlease enter this code to verify your email address.\n\nBest regards,\nPhilippine Association of Practioners of Student Affairs and Services'
                send_mail(subject, message, 'your_email@example.com', [user.email])

                # Set user as inactive until email is verified
                user.is_active = False
                user.save()

                # Redirect to email verification page
                return redirect('verify_email', user_id=user.id)
        else:
            return render(request, 'papsas_app/register.html', {
                'form': form,
                'message' : 'Invalid form data'
        })          
    else:
        return render(request, 'papsas_app/register.html', {
            'form': form,
        })

def logout_view(request):
    logout(request)
    return redirect('index')

def login_view(request):
    form = LoginForm()
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.email_verified:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, 'papsas_app/login.html', {
                    'message' : 'Please verify your email address before logging in.'
                })
        else:
            form = LoginForm(request.POST)
            return render(request, 'papsas_app/login.html', {
                'message' : 'Invalid Credentials',
                'form' : form
                })
    else:
        return render(request, 'papsas_app/login.html', {
            'form' : form
        })

def verify_email(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        code = request.POST['code']
        if user.verification_code == int(code):
            user.email_verified = True
            user.is_active = True
            user.save()
            # return render(request, 'papsas_app/layout.html', {'message': 'Email successfully verified!'})
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            # if user input wrong verification code, just bring them back to the 'verify_email'
            return render(request, 'papsas_app/verify_email.html', {
                'message' : 'Invalid Verification Code'
                })
            # return HttpResponse('Invalid verification code')
    else:
        return render(request, 'papsas_app/verify_email.html', {'user_id': user_id})
    
def election(request):
    electionList = Election.objects.all()
    ongoingElection = Election.objects.filter(electionStatus = True)
    if request.method == 'POST':
        newElection = Election(electionStatus = True, startDate = date.today())
        newElection.save()

    if is_officer(request):
        return render(request, "papsas_app/election.html", {
            'electionList' : electionList,
            'ongoingElection' : ongoingElection,
        })
    else:
        return redirect('index')


def is_officer(request):
    # check if user is officer
    today = date.today()
    user = request.user
    if user.is_authenticated:
        try:
            candidacy = Candidacy.objects.filter( candidate = user).latest('id')
            officer = Officer.objects.filter( candidateID = candidacy ).latest('id')
        except (Officer.DoesNotExist, Candidacy.DoesNotExist):
            officer = None
    else:
        officer = None

    if officer is not None and officer.termEnd > today:
        return True

    else:
        return False

        

def manage_election(request, id):
    if request.method == 'POST':
        election = Election.objects.get(id = id)
        if (election.electionStatus == True):
            election.electionStatus = False
            election.save()
            return redirect('election')
        
def vote(request):
    ongoingElection = Election.objects.filter( electionStatus = True ).latest('id')
    candidates = Candidacy.objects.filter( election = ongoingElection )
    return render(request, 'papsas_app/vote.html', {
        'candidates' : candidates,
    })

def profile(request, id):
    user = User.objects.get( id = id)
    form = ProfileForm()

    if request.method =='POST':
        # save the image as profilePic from 
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profilePic = form.cleaned_data['profilePic']
            user.profilePic = profilePic
            user.save()
            return redirect('profile', id = id)
    return render(request, 'papsas_app/profile.html/', {
        'viewUser' : user,
        'form' : form
    })

def event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('event')
        else:
            return render(request, 'papsas_app/event_management.html', {
                'form' : form
            })

    else:     
        form = EventForm
        return render(request, 'papsas_app/event_management.html', {
            'form' : form
        })

def attendance_form(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            event_id = form.cleaned_data['event_id']
            try:
                user = User.objects.get(id=user_id)
                event = Event.objects.get(id=event_id)
                # Check if the user is registered for the current event
                event_registration = EventRegistration.objects.filter(user=user, event=event)
                if event_registration.exists():
                    attendance, created = Attendance.objects.get_or_create(user=user, event=event)
                    attendance.attended = True
                    attendance.save()
                    return redirect('index')
                else:
                    return render(request, 'papsas_app/attendance_error.html', {'error': 'You are not registered for this event'})
            except User.DoesNotExist:
                return render(request, 'papsas_app/attendance_error.html', {'error': 'Invalid user ID'})
            except Event.DoesNotExist:
                return render(request, 'papsas_app/attendance_error.html', {'error': 'Invalid event ID'})
    else:
        form = AttendanceForm()
    return render(request, 'papsas_app/attendance_form.html', {'form': form})

def mark_attendance(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        user_id = request.POST['user_id']
        try:
            user = User.objects.get(id=user_id)
            attendance, created = Attendance.objects.get_or_create(user=user, event=event)
            attendance.attended = True
            attendance.save()
            return render(request, 'papsas_app/attendance_success.html')
        except User.DoesNotExist:
            return render(request, 'papsas_app/attendance_error.html', {'error': 'Invalid user ID'})
    return render(request, 'papsas_app/attendance_form.html', {'event': event})


@login_required
def event_registration_view(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        form = EventRegistrationForm(request.user, event, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = EventRegistrationForm(user=request.user, event=event)
    return render(request, 'papsas_app/event_registration_form.html', {'form': form, 'event': event})

def about(request):
    return render(request, 'papsas_app/about_us.html')

def become_member(request):
    memType = MembershipTypes.objects.all()
    return render(request, 'papsas_app/become_member.html', {
        'memType' : memType
    })

def news_offers(request):
    return render(request, 'papsas_app/news_offers.html')

def record(request):
    userRecord = User.objects.all()
    return render(request, 'papsas_app/record.html', {
        'userRecord' : userRecord
    })

def membership_registration(request, mem_id):
    user = request.user
    form = MembershipRegistration(request.user, mem_id)
    membership = mem_id

    try:
        is_member = user.member.get()
    except:
        is_member = None

    if request.method == 'POST':
        memType = MembershipTypes.objects.get( id = mem_id )
        form = MembershipRegistration(request.user, mem_id, data=request.POST, files = request.FILES)
        if form.is_valid():
            user_membership = form.save(commit=False)
            user_membership.user = request.user
            user_membership.membership_type = memType
            user_membership.save()

            if memType.duration is not None:
                user_membership.expirationDate = user_membership.registrationDate + memType.duration
            else:
                user_membership.expirationDate = None
            user_membership.save()
            return redirect('index')
        else:
            return render(request, 'papsas_app/membership_registration.html', {
            'form' : form,
            'membership' : membership
        })

    else:
        return render(request, 'papsas_app/membership_registration.html', {
            'form' : form,
            'membership' : membership,
            'is_member' : is_member
        })
    
def check_membership_validity(request):
    pass

def membership_record(request):
    record = UserMembership.objects.all()
    if is_officer(request):
        return render(request, 'papsas_app/membership_record.html', {
            'record' : record,
        })
    else:
        return redirect('index')
def approve_membership(request, id):
    userID = id
    if request.method == 'POST':
        user_membership = UserMembership.objects.get(user=userID)
        user_membership.membershipVerification = True
        user_membership.save()
        return redirect('membership_record')
    else:
        return render(request, 'papsas_app/index.html')
    
def decline_membership(request, id):
    userID = id
    if request.method == 'POST':
        user_membership = UserMembership.objects.get(user=userID)
        user_membership.delete()
        return redirect('membership_record')
