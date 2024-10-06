from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .models import User, Officer, Candidacy, Election, Event, Attendance, EventRegistration, MembershipTypes, UserMembership, Vote, Achievement, NewsandOffers, Venue
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random, json, logging
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from django.db.models.functions import TruncDay
from django.utils.dateformat import DateFormat
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import User, MembershipTypes, Vote, Event, Officer
from django.db import models
# Imported Forms
from .forms import AttendanceForm, EventRegistrationForm, EventForm, ProfileForm, RegistrationForm, LoginForm, MembershipRegistration, Attendance, VenueForm, AchievementForm, NewsForm, UserUpdateForm
from datetime import date, timedelta
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.db.models import Count, Avg
from django.core.exceptions import ObjectDoesNotExist
from functools import wraps
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def practitioner_required(view_func):
    @wraps(view_func)
    def decorated_view(request, *args, **kwargs):
        if request.user.occupation != 'Practitioner':
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return decorated_view

def index(request):
    today = date.today()
    events = Event.objects.all()
    upcoming_events = [event for event in events if event.startDate >= today]
    return render(request, 'papsas_app/index.html', {
        'events' : upcoming_events,
    })



def register(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
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
                    form.add_error('region', 'Please select a valid region.')
                if occupation == 'Occupation':
                    form.add_error('occupation', 'Please select a valid occupation.')

                if birthDate:
                    calculated_age = date.today().year - birthDate.year - ((date.today().month, date.today().day) < (birthDate.month, birthDate.day))
                    if age != calculated_age:
                        form.add_error('age', 'Birthdate and Age did not match. Please input the correct details')

                if not form.errors:
                    user = User.objects.create_user(
                        username=username,
                        email=username,
                        password=password,
                        first_name=fname,
                        last_name=lname,
                        mobileNum=mobileNum,
                        region=region,
                        address=address,
                        occupation=occupation,
                        age=age,
                        birthdate=birthDate
                    )

                    user.is_active = False
                    user.save()

                    return redirect('verify_email', user_id=user.id)

            except IntegrityError:
                form.add_error('email', 'A user with this email already exists.')

        return render(request, 'papsas_app/register.html', {
            'form': form,
            'message': 'Please correct the highlighted errors below.'
        })

    return render(request, 'papsas_app/register.html', {
        'form': form,
    })


def logout_view(request):
    logout(request)
    return redirect('index')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.email_verified and user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            elif not user.email_verified:
                return redirect('email_not_verified', user_id=user.id)
            else:
                form = LoginForm(request.POST)
                return render(request, 'papsas_app/login.html', {
                    'message' : 'Your account is not active.',
                    'form' : form
                })
        else:
            form = LoginForm(request.POST)
            return render(request, 'papsas_app/login.html', {
                'message' : 'Invalid Credentials',
                'form' : form
                })
    else:
        form = LoginForm()
        return render(request, 'papsas_app/login.html', {
            'form' : form
        })

def verify_email(request, user_id):
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        if 'resend_code' in request.POST:
            # Only resend the code if explicitly requested
            user.verification_code = random.randint(100000, 999999)
            user.verification_code_expiration = timezone.now() + timezone.timedelta(minutes=2)
            user.save()

            # Send email with the new verification code
            subject = 'Verify your email address'
            message = f'Dear {user.first_name},\n\nYour new verification code is: {user.verification_code}\n\nPlease enter this code to verify your email address.\n\nBest regards,\nPhilippine Association of Practioners of Student Affairs and Services'
            send_mail(subject, message, 'your_email@example.com', [user.email])
            
            return render(request, 'papsas_app/verify_email.html', {
                'message': 'A new verification code has been sent to your email address.',
                'user': user,
                'expiration_timestamp': int(user.verification_code_expiration.timestamp())
            })

        else:
            try:
                # Combine the six individual code inputs into a single string
                code = (
                    request.POST['code-1'] +
                    request.POST['code-2'] +
                    request.POST['code-3'] +
                    request.POST['code-4'] +
                    request.POST['code-5'] +
                    request.POST['code-6']
                )

                if user.verification_code_expiration and timezone.now() > user.verification_code_expiration:
                    return render(request, 'papsas_app/verify_email.html', {
                        'message': 'Verification code has expired. Please request a new one.',
                        'resend_code': True,
                        'user': user,
                        'expiration_timestamp': 0
                    })
                
                elif user.verification_code == int(code):
                    user.email_verified = True
                    user.is_active = True
                    user.save()
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))

                else:
                    return render(request, 'papsas_app/verify_email.html', {
                        'message': 'Invalid Verification Code',
                        'user': user,
                        'expiration_timestamp': int(user.verification_code_expiration.timestamp())
                    })

            except KeyError:
                # Handle missing input fields
                return render(request, 'papsas_app/verify_email.html', {
                    'message': 'Please fill in all digits of the verification code.',
                    'user': user,
                    'expiration_timestamp': int(user.verification_code_expiration.timestamp())
                })
    
    else:
        # Only generate a new code if it's missing or expired
        if (user.verification_code is None or 
            user.verification_code_expiration is None or 
            timezone.now() > user.verification_code_expiration):
            
            user.verification_code = random.randint(100000, 999999)
            user.verification_code_expiration = timezone.now() + timezone.timedelta(minutes=2)
            user.save()

            # Send email with the new verification code
            subject = 'Verify your email address'
            message = f'Dear {user.first_name},\n\nYour verification code is: {user.verification_code}\n\nPlease enter this code to verify your email address.\n\nBest regards,\nPhilippine Association of Practioners of Student Affairs and Services'
            send_mail(subject, message, 'your_email@example.com', [user.email])

        # Pass the expiration timestamp to the template
        return render(request, 'papsas_app/verify_email.html', {
            'user': user,
            'expiration_timestamp': int(user.verification_code_expiration.timestamp())
        })
    
def email_not_verified(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, 'papsas_app/email_not_verified.html', {
        'user_id': user_id
    })
    
def resend_verification_code(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        verification_code = random.randint(100000, 999999)
        user.verification_code = verification_code
        user.verification_code_generated_at = timezone.now()
        user.save()
        subject = 'Verify your email address'
        message = f'Dear {user.first_name},\n\nYour verification code is: {verification_code}\n\nPlease enter this code to verify your email address.\n\nBest regards,\nPhilippine Association of Practioners of Student Affairs and Services'
        send_mail(subject, message, 'your_email@example.com', [user.email])
        return redirect('verify_email', user_id=user.id)
    return redirect('login')


def election(request):
    
    electionList = Election.objects.all()
    ongoingElection = Election.objects.filter(electionStatus = True)
    if request.method == 'POST':
        num_winners = request.POST['num_candidates']
        title = request.POST['title']
        newElection = Election(electionStatus = True, startDate = date.today(), title = title, numWinners = num_winners,)
        newElection.save()

    if is_officer(request):
        return render(request, "papsas_app/record/election.html", {
            'electionList' : electionList,
            'ongoingElection' : ongoingElection,
        })
    else:
        return redirect('index')
    
def manage_election(request, id):
    if request.method == 'POST':
        election = Election.objects.get(id = id)
        numWinners = election.numWinners
        new_officer(numWinners)
        if (election.electionStatus == True):
            election.electionStatus = False
            election.save()
            return redirect('election')

def new_officer(num_winners):
    try:
        ongoing_election = Election.objects.get(electionStatus=True)
    except Election.DoesNotExist:
        print("No ongoing election found")
        return

    top_candidates = Candidacy.objects.filter(election=ongoing_election).annotate(vote_count=Count('nominee')).order_by('-vote_count')[:num_winners]
    
    for candidate in top_candidates[:num_winners]:
        officer = Officer(
            candidateID=candidate,
            position='Regular',
            termStart=date.today(),
            termEnd=date.today() + timedelta(days=365)
        )
        officer.save()


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

@practitioner_required
def vote(request):
    user = request.user
    ongoingElection = Election.objects.get( electionStatus = True )
    attended_event = Attendance.objects.filter( user = user, attended = True )
    # candidates = Candidacy.objects.filter( election = ongoingElection )
    candidates = Candidacy.objects.filter(election=ongoingElection).annotate(vote_count=Count('nominee'))


    if request.POST:
        selected_candidates = request.POST.getlist('candidates')

        if not selected_candidates:
            return HttpResponse("No candidate selected!" , status=400)
        try:
            user_voted = Vote.objects.filter( voterID = user, election = ongoingElection)
        except Vote.DoesNotExist:
            user_voted = None
        if user_voted:
            return HttpResponse("You have already voted!" , status=400)

        vote = Vote.objects.create(voterID=user, election = ongoingElection)
        num_selected = len(selected_candidates)
        req_selected = ongoingElection.numWinners
        if num_selected <= req_selected:
            for candidate_id in selected_candidates:
                try:
                    candidate_obj = Candidacy.objects.get(id = candidate_id, election = ongoingElection)
                    vote.candidateID.add(candidate_obj)
                except Candidacy.DoesNotExist:
                    # handle the case where the candidate does not exist
                    return HttpResponse("Invalid candidate!", status=400)
        else:
            return render(request, 'papsas_app/form/vote.html', {
                'message' : 'You voted above the limit'
            })
        return redirect('index')
    else:
        return render(request, 'papsas_app/form/vote.html', {
            'candidates' : candidates,
            'attended_event' : attended_event,
            'ongoingElection' : ongoingElection,
            'votes' : Vote.objects.filter( voterID = user, election = ongoingElection),

        })

def profile(request, id):
    candidacies = Candidacy.objects.filter( candidate = id )
    attended_event = Attendance.objects.filter( user = id )
    elected_officer = Officer.objects.filter(candidateID__candidate= id)
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
        'form' : form,
        'candidacies' : candidacies,
        'attended_events' : attended_event,
        'elected_officers' : elected_officer
    })
logger = logging.getLogger(__name__)
def event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            exclusive = request.POST.get('exclusive', False)
            if exclusive == 'on':
                exclusive = True
            else:
                exclusive = False
            event.exclusive = exclusive
            event.save()

            subject = f'Don’t Miss Out: Exciting New Event: {event.eventName}'
            message_template = (
                'Dear {name},\n\n'
                'We hope this message finds you well! We are thrilled to announce an upcoming event hosted by the Philippine Association of Practitioners of Student Affairs and Services (PAPSAS) that promises to be both enriching and transformative.\n\n'
                '📅 Event Details:\n'
                f'- Event Name: {event.eventName}\n'
                f'- Date: {event.startDate}\n'
                f'- Time: {event.startTime}\n'
                f'- Venue: {event.venue}\n\n'
                'This is not just another event; it’s a chance to elevate your practice and make meaningful connections. Don’t wait too long! Spaces are limited, and we want to ensure that you are part of this unique experience.\n\n'
                'Feel free to share this event with your colleagues—let’s grow together as a community!\n\n'
                'Thank you for being an integral part of PAPSAS. We look forward to seeing you there!\n\n'
                'Warm regards,\n'
                '[Bien]\n'  # Replace with actual sender's name
                '[Pogi sa Pinas]\n'
                'Philippine Association of Practitioners of Student Affairs and Services\n'
            )
            #dito ichcheck kung email_verified at kung practitioner or student
            if event.exclusive:
                users_to_email = User.objects.filter(email_verified=True)
            else:
                users_to_email = User.objects.filter(occupation='Practitioner', email_verified=True)

            for user in users_to_email:
                message = message_template.format(name=user.first_name, event_name=event.eventName)
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                except Exception as e:
                    logger.error("Error sending email: %s", e)


            return redirect('index')
    else:
        form = EventForm
    return render(request, 'papsas_app/event_management.html', {'form': form})

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
    return render(request, 'papsas_app/form/attendance_form.html', {'form': form})

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
    return render(request, 'papsas_app/form/attendance_form.html', {'event': event})


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
    return render(request, 'papsas_app/form/event_registration_form.html', {'form': form, 'event': event})

def about(request):
    return render(request, 'papsas_app/view/about_us.html')

def become_member(request):
    memType = MembershipTypes.objects.all()
    return render(request, 'papsas_app/view/become_member.html', {
        'memType' : memType
    })

def news_offers(request):
    news_offers = NewsandOffers.objects.all()
    return render(request, 'papsas_app/view/news_offers.html', {
        'news_offers' : news_offers
    })

def record(request):
    try:
        form = RegistrationForm()
        userRecord = User.objects.all()

        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('index')
            else:
                return render(request, 'papsas_app/form/record_form.html', 
                              {'form': form
                })
        return render(request, 'papsas_app/record.html', {
            'form' : form,
            'userRecord' : userRecord
        })
    except:
        return HttpResponseNotFound('Page not Found!')
    
def update_account(request, id):
    try:
        user = User.objects.get(id=id)
        form = UserUpdateForm(instance=user)
        if request.method == 'POST':
            form = UserUpdateForm(request.POST, instance = user )
            if form.is_valid():
                form.save()
                return redirect('record')
            else:
                errors = form.errors.as_json()
                return HttpResponse(errors, content_type='application/json')

    except Exception as e:
        return HttpResponseForbidden(f'Error: {e}')

    
def membership_registration(request, mem_id):
    form = MembershipRegistration(request.user, mem_id)
    membership = mem_id

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
            return render(request, 'papsas_app/form/membership_registration.html', {
            'form' : form,
            'membership' : membership
        })

    else:
        return render(request, 'papsas_app/form/membership_registration.html', {
            'form' : form,
            'membership' : membership,
        })
    
def check_membership_validity(request):
    pass

def membership_record(request):
    record = UserMembership.objects.all()
    if is_officer(request):
        return render(request, 'papsas_app/record/membership_record.html', {
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
        if user_membership.membershipVerification == True:
            user_membership.membershipVerification = False
            user_membership.save()
            return redirect('membership_record')
        else:
            return redirect('membership_record')
    
def delete_membership(request, id):
    userID = id
    if request.method == 'POST':
        user_membership = UserMembership.objects.get(user=userID)
        if user_membership.membershipVerification == False:
            user_membership.delete()
            return redirect('membership_record')
        else:
            return redirect('membership_record')

def get_user_info(request, id):
    user = User.objects.get(id = id)
    user_data = {
        'username' : user.email,
        'firstName' : user.first_name,
        'lastName' : user.last_name,
        'mobileNum' : user.mobileNum,
        'region' : user.region,
        'address' : user.address,
        'occupation' : user.occupation,
        'age' : user.age,
        'birthdate' : user.birthdate,
        'institution' : user.institution,
    }
    return JsonResponse (user_data)
    
def event_calendar(request):
    events = Event.objects.all().order_by('startDate')
    data = []
    for event in events:
        data.append({
            'title': event.eventName,
            'start': event.startDate,
            'end': event.endDate
        })
    return render(request, 'papsas_app/event_calendar.html', {'events': data})

# Password Reset Request View (Sends Verification Code)
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate new verification code if it is missing or expired
            if (user.verification_code is None or 
                user.verification_code_expiration is None or 
                timezone.now() > user.verification_code_expiration):
                
                user.verification_code = random.randint(100000, 999999)
                user.verification_code_expiration = timezone.now() + timedelta(minutes=2)
                user.save()

                # Send email with the new verification code
                subject = 'Password Reset Verification Code'
                message = f'Dear {user.first_name},\n\nYour verification code is: {user.verification_code}\n\nPlease enter this code to reset your password.\n\nBest regards,\nPhilippine Association of Practioners of Student Affairs and Services'
                send_mail(subject, message, 'your_email@example.com', [user.email])

            return redirect('password_reset_verify', user_id=user.id)

        except ObjectDoesNotExist:
            messages.error(request, 'User with this email does not exist.')
            return redirect('password_reset')

    else:
        form = PasswordResetForm()
        form.fields['email'].widget.attrs['placeholder'] = 'Enter your email address'
        form.fields['email'].widget.attrs['class'] = 'password-reset'
        return render(request, 'papsas_app/password_reset.html', {'form': form})


def password_reset_verify(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        if 'resend_code' in request.POST:
            # Resend the verification code
            user.verification_code = random.randint(100000, 999999)
            user.verification_code_expiration = timezone.now() + timezone.timedelta(minutes=2)
            user.save()

            # Send email with the new verification code
            subject = 'Password Reset Verification Code'
            message = f'Dear {user.first_name},\n\nYour new verification code is: {user.verification_code}\n\nPlease enter this code to reset your password.\n\nBest regards,\nPhilippine Association of Practitioners of Student Affairs and Services'
            send_mail(subject, message, 'your_email@example.com', [user.email])

            # Provide feedback message
            return render(request, 'papsas_app/password_reset_verify.html', {
                'message': 'A new verification code has been sent to your email address.',
                'user': user,
                'resend_code': False,  # Initially hide the resend button
                'expiration_timestamp': int(user.verification_code_expiration.timestamp())
            })

        else:
            # Combine the six individual code inputs into a single string
            code = (
                request.POST['code-1'] +
                request.POST['code-2'] +
                request.POST['code-3'] +
                request.POST['code-4'] +
                request.POST['code-5'] +
                request.POST['code-6']
            )

            if user.verification_code_expiration and timezone.now() > user.verification_code_expiration:
                return render(request, 'papsas_app/password_reset_verify.html', {
                    'message': 'Verification code has expired. Please request a new one.',
                    'resend_code': True,  # Show the resend button
                    'user': user,
                    'expiration_timestamp': 0
                })

            elif user.verification_code == int(code):
                return redirect('password_reset_confirm', user_id=user.id)

            else:
                return render(request, 'papsas_app/password_reset_verify.html', {
                    'message': 'Invalid Verification Code',
                    'user': user,
                    'resend_code': False,
                    'expiration_timestamp': int(user.verification_code_expiration.timestamp())
                })

    # Handle GET request to display the form
    if user.verification_code_expiration is None or timezone.now() > user.verification_code_expiration:
        user.verification_code = random.randint(100000, 999999)
        user.verification_code_expiration = timezone.now() + timezone.timedelta(minutes=2)
        user.save()

        # Only send the email when a new code is generated
        subject = 'Password Reset Verification Code'
        message = f'Dear {user.first_name},\n\nYour verification code is: {user.verification_code}\n\nPlease enter this code to reset your password.\n\nBest regards,\nPhilippine Association of Practitioners of Student Affairs and Services'
        send_mail(subject, message, 'your_email@example.com', [user.email])

        message_context = 'A new verification code has been sent to your email address.'
    else:
        message_context = 'You still have a valid verification code.'

    return render(request, 'papsas_app/password_reset_verify.html', {
        'user': user,
        'resend_code': False,  # Initially hide the resend button
        'expiration_timestamp': int(user.verification_code_expiration.timestamp()),
        'message': message_context  # Pass the appropriate message based on code generation
    })

def password_reset_confirm(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            user.set_password(password1)
            user.save()
            return redirect('login')
        else:
            return render(request, 'papsas_app/password_reset_confirm.html', {'message': 'Passwords do not match'})
    return render(request, 'papsas_app/password_reset_confirm.html', {'user_id': user_id})

def count_vote(id):
    candidate = Candidacy.objects.get(id= id)  # replace with the actual candidate id
    num_votes = candidate.vote_set.count()

    return num_votes

def compose_venue(request):
    form = VenueForm()

    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('compose_venue')
    return render(request, 'papsas_app/form/compose_venue.html', {
        'form': form,
    })

def event_list(request):
    events = Event.objects.all()

    return render(request, 'papsas_app/view/event_view.html', {
        'events': events,
    })

def attendance_list(request):
    events = Event.objects.all()
    form = EventForm()
    return render(request, 'papsas_app/record/attendance_record.html', {
        'events': events,
        'form': form,
    })

def get_receipt(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_registration = UserMembership.objects.get(user=user)
        receipt = user_registration.receipt.url
        receipt_data = {
            'receipt': receipt
        }
        return JsonResponse(receipt_data)
    
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'User or UserMembership not found'}, status=404)
    
def get_id(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_registration = UserMembership.objects.get(user=user)
        id = user_registration.verificationID.url
        id_data = {
            'id': id
        }
        return JsonResponse(id_data)
    
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'User or UserMembership not found'}, status=404)

def get_officers(request, election_id):
    try:
        election = Election.objects.get( id = election_id)
    except Election.DoesNotExist:
        return HttpResponseNotFound("Election not found")
    
    candidates = Candidacy.objects.filter( election = election )
    num_officers = election.numWinners

    data = []
    for candidate in candidates:
        total_votes = Vote.objects.filter(candidateID = candidate).count()
        data.append({
            'name': f'{candidate.candidate.first_name} {candidate.candidate.last_name}',
            'total_votes' : total_votes,
        })


    return JsonResponse({'officers': data, 'num_elected' : num_officers})

def compose_achievement(request):
    form = AchievementForm()

    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            return render(request, 'papsas_app/form/compose_achievement.html', {
                'form' : form,
            })
        
    return render(request, 'papsas_app/form/compose_achievement.html', {
        'form' : form
    })

def compose_news_offer(request):
    form = NewsForm()

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            return render(request, 'papsas_app/form/compose_news_offers.html', {
                'form' : form,
            })

    return render(request, 'papsas_app/form/compose_news_offers.html', {
        'form' : form
    })

def achievement_view(request):
    achievements = Achievement.objects.all()
    return render(request, 'papsas_app/view/achievement_view.html', {
        'achievements' : achievements,
    } )

def venue_record(request):
    venues = Venue.objects.all()
    form = VenueForm()
    return render(request, 'papsas_app/record/venue_record.html', {
        'venues' : venues,
        'form' : form,
    })

def achievement_record(request):
    achievements = Achievement.objects.all()
    form = AchievementForm()
    return render(request, 'papsas_app/record/achievement_record.html', {
        'achievements' : achievements,
        'form' : form,
    })

def get_achievement_data(request, achievement_id):
    try:
        achievement = Achievement.objects.get( id = achievement_id )
        if request.method =="POST":
            form = AchievementForm( request.POST, request.FILES, instance = achievement )
            if form.is_valid():
                form.save()
                return redirect('achievement_record')
            else:
                return JsonResponse({'error': 'Invalid request'}, status=400)   

        data = {
            'name' : achievement.name,
            'description' : achievement.description,
            'pubmat' : achievement.pubmat.url,
        }
        return JsonResponse(data)
    
    except Achievement.DoesNotExist:
        return JsonResponse({'error' : 'Achievement not found'}, status = 404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def update_news_offer(request, id):
    try:
        news_offer = NewsandOffers.objects.get( id = id)
        if request.method == "POST":
            form = NewsForm( request.POST, request.FILES, instance=news_offer)
            if form.is_valid():
                news_offer.name = request.POST.get('name')
                news_offer.description = request.POST.get('description')
                if request.FILES.get('pubmat') is not None:
                    news_offer.pubmat = request.FILES.get('pubmat')
                else:
                    news_offer.pubmat = news_offer.pubmat
                news_offer.save()
                return redirect('news_offers_record')
            else:
                return JsonResponse({'error': 'Invalid request'}, status=400)
        data = {
            'name' : news_offer.name,
            'description' : news_offer.description,
            'pubmat' : news_offer.pubmat.url,
            }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error' : e}, status = 404)
    
def delete_achievement(request, id):
    try:
        achievement = Achievement.objects.get( id = id )
        achievement.delete()
        messages.success(request, 'Achievement deleted successfully!')
        return redirect('achievement_record')
    except Achievement.DoesNotExist:
        return HttpResponseNotFound('Achievement not found')

    except Exception as e:
        return HttpResponse(f'Error: {e}')

def news_offers_record(request):
    news_offers = NewsandOffers.objects.all()
    form = NewsForm()
    return render(request, 'papsas_app/record/news_offers_record.html', {
        'news_offers' : news_offers,
        'form' : form,
        })


def delete_account(request, id):
    try:
        accounts = User.objects.all()
        user = User.objects.get( id = id)
        
        if request.method == 'POST':
            user.is_active = False
            user.save()
            return render(request, 'papsas_app/record.html', {
                'userRecord' : accounts
            })
    except:
        return HttpResponseNotFound('User not Found')

#htmx functions
def get_account(request):
    userRecord = User.objects.all()
    return render(request, 'papsas_app/partial_list/account_list.html', {
        'userRecord' : userRecord
    }) 

def get_attendees(request, event_id):
    try:
        eventId = Event.objects.get(id=event_id)
        attendances = Attendance.objects.filter(event__event_id=eventId)
        attendees = []
        for attendance in attendances:
            attendees.append({
                'username': attendance.user.username,
                'first_name': attendance.user.first_name,
                'last_name': attendance.user.last_name,
                'status' : attendance.attended
            })
        return render(request, 'papsas_app/partial_list/attendance_list.html', {
            'attendees': attendees,
            'eventId' : eventId
            })
    except Event.DoesNotExist:
        return render(request, 'papsas_app/partial_list/attendance_list.html', {'attendees': []})

def get_event(request, view):
    events = Event.objects.all()
    return render(request, 'papsas_app/partial_list/event_list.html', {
        'events': events,
        'view' :view
        })

def get_venue(request):
    venues = Venue.objects.all()
    return render(request, 'papsas_app/partial_list/venue_list.html', {
        'venues': venues,
        })

def get_achievement(request):
    achievements = Achievement.objects.all()
    return render(request, 'papsas_app/partial_list/achievement_list.html', {
        'achievements' : achievements,
        })

def get_news_offers(request):
    news_offers = NewsandOffers.objects.all()
    return render(request, 'papsas_app/partial_list/news_offers_list.html', {
        'news_offers' : news_offers,
        })

def get_profile(request, id):
    candidacies = Candidacy.objects.filter( candidate = id )
    attended_event = Attendance.objects.filter( user = id )
    elected_officer = Officer.objects.filter(candidateID__candidate= id)
    user = User.objects.get( id = id)
    form = ProfileForm()
        
    return render(request, 'papsas_app/partial_list/profile_list.html/', {
        'viewUser' : user,
        'form' : form,
        'candidacies' : candidacies,
        'attended_events' : attended_event,
        'elected_officers' : elected_officer
    })

def get_event_reg(request, id):
    event = Event.objects.get(id = id)
    eventReg = EventRegistration.objects.filter(event = event)

    eventReg_data = []
    for reg in eventReg:
        eventReg_data.append({
            'id' : reg.id,
            'name' : f'{reg.user.first_name} {reg.user.last_name}',
            'receipt' : reg.receipt.url if reg.receipt else None,
            'status' : reg.status
        })
    return JsonResponse(eventReg_data, safe=False)

#admin dashboard


def admin_dashboard(request):
    return render(request, 'papsas_app/admin_dashboard.html')

def get_attendance_per_venue(request):
    venue_attendance = {}
    
    for attendance in Attendance.objects.select_related('event'):
        venue_name = attendance.event.event.venue.name
        if venue_name not in venue_attendance:
            venue_attendance[venue_name] = 0
        venue_attendance[venue_name] += 1

    data = {
        'labels': list(venue_attendance.keys()),
        'values': list(venue_attendance.values())
    }
    
    return JsonResponse(data)

def get_attendance_vs_capacity(request):
    try:
        attendance_data = (
            Attendance.objects
            .select_related('event')
            .values('event__event__venue__id', 'event__event__venue__name')
            .annotate(
                attendance_count=models.Count('id'),
                event_count=models.Count('event__event', distinct=True)
            )
        )

        venue_names = []
        average_attendance = []
        capacities = []

        for attendance in attendance_data:
            venue_id = attendance['event__event__venue__id']
            venue_name = attendance['event__event__venue__name']
            total_attendance = attendance['attendance_count']
            event_count = attendance['event_count']
            venue_capacity = Venue.objects.get(id=venue_id).capacity
            
            avg_attendance = total_attendance / event_count if event_count > 0 else 0

            venue_names.append(venue_name)
            average_attendance.append(round(avg_attendance, 2))
            capacities.append(venue_capacity)

        return JsonResponse({
            'labels': venue_names,
            'average_attendance': average_attendance,
            'capacities': capacities
        })
    except Exception as e:
        logging.error("Error fetching attendance vs capacity data: %s", e)
        return JsonResponse({'error': str(e)}, status=500)

def get_membership_distribution_data(request):
    membership_data = UserMembership.objects.values('membership__type').annotate(total=Count('membership')).order_by('-total')
    
    labels = [item['membership__type'] for item in membership_data]
    values = [item['total'] for item in membership_data]
    
    return JsonResponse({
        'labels': labels,
        'values': values,
    })

def get_attendance_over_time_data(request):
    data = {"labels": [], "values": []}
    
    attendances = Attendance.objects.filter(attended=True)
    attendances_by_day = attendances.annotate(day=TruncDay('date_attended')).values('day').annotate(count=Count('id')).values_list('day', 'count')
    
    for day, count in attendances_by_day:
        data["labels"].append(day.strftime("%Y-%m-%d"))
        data["values"].append(count)
    
    return JsonResponse(data)

def get_total_events_count(request):
    total_events = Event.objects.count()
    return JsonResponse({'total_events': total_events})

def get_total_members_count(request):
    total_members = UserMembership.objects.count()
    return JsonResponse({'count': total_members})

def get_total_events_count(request):
    count = Event.objects.count() 
    return JsonResponse({'count': count})

def get_total_revenue(request):
    total_revenue = 0
    events = Event.objects.all()  # Get all events

    for event in events:
        registrations_count = event.activity.count()  # Count how many registrations for each event
        if event.price:  # Ensure the price is not None
            total_revenue += event.price * registrations_count  # Multiply price by number of registrations

    return JsonResponse({'total_revenue': total_revenue})

def get_membership_growth(request):
    today = timezone.now()
    start_year = today.year - 10  # Adjust to how many years you want to show

    # Count new members by year
    growth_data = (
        User.objects.filter(date_joined__year__gte=start_year)
        .extra(select={'year': 'date_joined::date'})
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )

    # Prepare the response data
    labels = []
    values = []
    for data in growth_data:
        labels.append(data['year'].strftime('%Y'))  # Format the year
        values.append(data['count'])

    # Ensure all years in range are included, with 0 if no members
    for year in range(start_year, today.year + 1):
        if year not in [int(label) for label in labels]:
            labels.append(str(year))
            values.append(0)

    # Sort by year
    sorted_data = sorted(zip(labels, values))
    sorted_labels, sorted_values = zip(*sorted_data)

    return JsonResponse({'labels': list(sorted_labels), 'values': list(sorted_values)})

def get_avg_registration_vs_attendance(request):
    avg_registrations = EventRegistration.objects.count()
    avg_attendances = Attendance.objects.filter(attended=True).count()

    total_events = Event.objects.count()
    if total_events > 0:
        overall_avg_registration = avg_registrations / total_events
        overall_avg_attendance = avg_attendances / total_events
    else:
        overall_avg_registration = 0
        overall_avg_attendance = 0

    data = {
        'labels': ['Average Registration', 'Average Attendance'],
        'values': [overall_avg_registration, overall_avg_attendance]
    }

    return JsonResponse(data)

def get_top_region_data(request):
    top_regions = User.objects.values('region').annotate(count=models.Count('id')).order_by('-count')[:5]
    labels = [region['region'] for region in top_regions]
    values = [region['count'] for region in top_regions]
    return JsonResponse({'labels': labels, 'values': values})

def get_least_region_data(request):
    least_regions = User.objects.values('region').annotate(count=models.Count('id')).order_by('count')[:5]
    labels = [region['region'] for region in least_regions]
    values = [region['count'] for region in least_regions]
    return JsonResponse({'labels': labels, 'values': values})

@csrf_exempt
def decline_eventReg(request, id):
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("status") is not None:
            eventReg = EventRegistration.objects.get( id = id)
            eventReg.status = data["status"]
            eventReg.save()
            return JsonResponse({'message': 'Updated successfully!'}, status = 200)
    return JsonResponse({'error': 'Only PUT method is allowed.'}, status=405)
    
@csrf_exempt
def approve_eventReg(request, id):
    eventReg = EventRegistration.objects.get( id = id)
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("status") is not None:
            eventReg.status = data["status"]
            eventReg.save()
            return JsonResponse({'message': 'Updated successfully!'}, status = 200)
    return JsonResponse({'error': 'Only PUT method is allowed.'}, status=405)

def delete_news_offer(request, id):
    try:
        news_offer = NewsandOffers.objects.get(id = id)
        news_offer.delete()
        messages.success(request, 'Deleted successfully!')
        return redirect('news_offers_record')
    except Exception as e:
        return render(request, 'papsas_app/record/news_offers_record.html', {
            'error': f'Error found: {e}',
        })
    
def delete_venue(request, id):
    try:
        venue = Venue.objects.get(id = id)
        if request.method == "POST":
            venue.delete()
            messages.success(request, 'Deleted successfully!')
            return redirect('venue_record')
    except Exception as e:
        return render(request, 'papsas_app/record/venue_record.html', {
            'error': f'Error found: {e}',
            })
    
def update_venue(request, id):
    try:
        venue = Venue.objects.get(id = id)
        if request.method == "POST":
            form = VenueForm(request.POST, instance = venue)
            if form.is_valid():
                form.save()
                messages.success(request, 'Updated successfully!')
                return redirect('venue_record')
            else:
                return render(request, 'papsas_app/record/venue_record.html', {
                    'error': 'Invalid form data.',
                    'form': form,
                    })
        data = {
            'name' : venue.name,
            'address' : venue.address,
            'capacity' : venue.capacity,
            }
        return JsonResponse(data)
        
    except Exception as e:
        return render(request, 'papsas_app/record/venue_record.html', {
            'error': f'Error found: {e}',
            })

def delete_event (request, id):
    try:
        event = Event.objects.get(id = id)
        if request.method == "POST":
            event.delete()
            messages.success(request, 'Deleted successfully!')
            return redirect('attendance_list')

    except Exception as e:
        return render(request, 'papsas_app/record/attendance_record.html', {
            'error': f'Error found: {e}',
            })

def update_event (request, id):
    try:
        event = Event.objects.get(id = id)
        if request.method == "POST":
            form = EventForm(request.POST, request.FILES, instance = event)
            if form.is_valid:
                form.save()
                messages.success(request, 'Updated successfully!')
                return redirect('attendance_list')
            else:
                return render(request, 'papsas_app/record/attendance_record.html', {
                    'error': 'Invalid form data.',
                    'form': form,
                    })
        data = {
            'name' : event.eventName,
            'startDate' : event.startDate,
            'endDate' : event.endDate,
            'venue' : event.venue.id,
            'exclusive' : event.exclusive,
            'description' : event.eventDescription,
            'pubmat' : event.pubmat.url,
            'price' : event.price,
            'startTime' : event.startTime,
            'endTime' : event.endTime,
        }
        return JsonResponse(data)
    except Exception as e:
        return render(request, 'papsas_app/record/attendance_record.html', {
            'error': f'Error found: {e}',
            })
