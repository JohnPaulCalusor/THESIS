from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, logout, authenticate
from .models import User, Officer, Candidacy, Election, Event, Attendance, EventRegistration, MembershipTypes, UserMembership, Vote, Achievement, NewsandOffers, Venue, EventRating
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseNotAllowed
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django_tables2.paginators import LazyPaginator
from django.utils.html import strip_tags
import random, json, logging, qrcode
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from django.db.models.functions import TruncDay
from django.utils.dateformat import DateFormat
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import User, MembershipTypes, Vote, Event, Officer
from django.db import models
from django.contrib.auth.hashers import make_password
# Imported Forms
from .forms import AttendanceForm, EventRegistrationForm, EventForm, ProfileForm, RegistrationForm, LoginForm, MembershipRegistration, Attendance, VenueForm, AchievementForm, NewsForm, UserUpdateForm, EventRatingForm, TORForm, ProfileUpdateForm
from datetime import date, timedelta
from django.contrib.auth.forms import PasswordResetForm
from io import BytesIO
from django.contrib.auth.views import PasswordResetView
from django.db.models import Count, Avg, Q
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import TruncYear
from functools import wraps
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django_tables2 import SingleTableView, RequestConfig, SingleTableMixin
from .tables import UserTable, MembershipTable, EventTable, EventRegistrationTable, EventAttendanceTable, VenueTable, AchievementTable, NewsAndOfferTable, UserMembershipTable, UserEventRegistrationTable, UserEventAttendanceTable, ElectionTable, VoteTable, FeedbackTable
from .filters import UserFilter, ElectionFilter, MembershipFilter, EventFilter, EventRegistrationFilter, AttendanceFilter, VenueFilter, AchievementFilter, NewsAndOfferFilter, CandidateFilter, FeedbackFilter
from django_filters.views import FilterView
from django.contrib.auth.password_validation import validate_password


# Create your views here.

def is_member(request):
    today = date.today()
    user = request.user
    if user.is_authenticated:
        try:
            membership = UserMembership.objects.filter(user=user).latest('id')
            if membership.status == 'Approved':
                return True
            else:
                return False
        except:
            return False
        
def is_officer(request):
    # check if user is officer
    today = date.today()
    user = request.user
    if user.is_authenticated:
        try:
            candidacy = Candidacy.objects.filter( candidate = user).latest('id')
            officer = Officer.objects.filter( candidateID = candidacy).latest('id')
        except (Officer.DoesNotExist, Candidacy.DoesNotExist):
            officer = None
    else:
        officer = None

    if officer is not None and officer.termEnd > today:
        return True

    else:
        return False

def is_secretary(request):
    today = date.today()
    user = request.user
    if user.is_authenticated:
        try:
            candidacy = Candidacy.objects.filter( candidate = user).latest('id')
            officer = Officer.objects.filter( candidateID = candidacy, position = 'Secretary' ).latest('id')
        except (Officer.DoesNotExist, Candidacy.DoesNotExist):
            officer = None
    else:
        officer = None

    if officer is not None and officer.termEnd > today:
        return True

    else:
        return False
    
def member_required(view_func):
    @wraps(view_func)
    def decorated_view(request, *args, **kwargs):
        if is_member(request):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return decorated_view

def member_or_officer_required(view_func):
    @wraps(view_func)
    def decorated_view(request, *args, **kwargs):
        print(f"is_member: {is_member(request)}")
        print(f"is_officer: {is_officer(request)}")
        if is_member(request) or is_officer(request):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return decorated_view


def practitioner_required(view_func):
    @wraps(view_func)
    def decorated_view(request, *args, **kwargs):
        if request.user.occupation != 'Practitioner':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return decorated_view

def officer_required(view_func):
    @wraps(view_func)
    def decorated_view(request, *args, **kwargs):
        if is_officer(request):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return decorated_view

def secretary_required(view_func):
    @wraps(view_func)
    def decorated_view(request, *args, **kwargs):
        if is_secretary(request):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return decorated_view

def index(request):
    today = date.today()
    events = Event.objects.all()
    upcoming_events = [event for event in events if event.startDate >= today]
    if is_secretary(request):
        return render(request, 'papsas_app/admin_dashboard.html')
    elif is_officer(request):
        return render(request, 'papsas_app/record/venue_table.html')
    else:
        return render(request, 'papsas_app/index.html', {
            'events' : upcoming_events,
        })

@member_required
def rate_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    existing_rating = EventRating.objects.filter(event=event, user=request.user).first()

    if request.method == 'POST':
        if existing_rating:
            form = EventRatingForm(request.POST, instance=existing_rating)
        else:
            form = EventRatingForm(request.POST)

        if form.is_valid():
            rating = form.save(commit=False)
            rating.event = event
            rating.user = request.user
            rating.updated_at = timezone.now()
            rating.save()
            messages.success(request, 'Feedback submitted successfully.')
            
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('user_event_registration_table')
                return response
            return redirect('user_event_registration_table')
    else:
        if existing_rating:
            form = EventRatingForm(instance=existing_rating)
        else:
            form = EventRatingForm()
    return render(request, 'papsas_app/rate_event.html', {'form': form, 'event': event})

# kulang tor
def register(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                fname = form.cleaned_data['first_name']
                lname = form.cleaned_data['last_name']
                mobileNum = form.cleaned_data['mobileNum']
                region = form.cleaned_data['region']
                address = form.cleaned_data['address']
                occupation = form.cleaned_data['occupation']
                age = form.cleaned_data['age']
                birthDate = form.cleaned_data['birthdate']
                institution = form.cleaned_data['institution']

                if region == 'Region':
                    form.add_error('region', 'Select a valid region.')
                if occupation == 'Occupation':
                    form.add_error('occupation', 'Select a valid occupation.')

                if birthDate:
                    calculated_age = date.today().year - birthDate.year - ((date.today().month, date.today().day) < (birthDate.month, birthDate.day))
                    if age != calculated_age:
                        form.add_error('age', 'Birthdate and Age did not match. Please input the correct details')

                if not form.errors:
                    user = User(
                        username=email,
                        email=email,
                        first_name=fname,
                        last_name=lname,
                        mobileNum=mobileNum,
                        region=region,
                        address=address,
                        occupation=occupation,
                        age=age,
                        birthdate=birthDate,
                        is_active = True,
                        institution = institution,
                    )
                    user.set_password(password)
                    user.save()

                    return redirect('verify_email', user_id=user.id)

            except IntegrityError:
                form.add_error('email', 'A user with this email already exists.')

        return render(request, 'papsas_app/register.html', {
            'form': form,
            'message': 'Enter valid input.'
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
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
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
                'message' : 'Invalid email and/or password',
                'form' : form
                })
    else:
        form = LoginForm()
        return render(request, 'papsas_app/login.html', {
            'form' : form
        })

def verify_email(request, user_id):
    try:  
        user = User.objects.get(id=user_id)
    except:
        return HttpResponseNotFound()
    
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

@secretary_required
def election(request):
    electionList = Election.objects.all()
    ongoingElection = Election.objects.filter(electionStatus=True)

    filter = ElectionFilter(request.GET, queryset=electionList)
    table = ElectionTable(filter.qs)

    RequestConfig(request, paginate={"per_page": 10}).configure(table)

    if request.method == 'POST':
        num_winners = request.POST['num_candidates']
        title = request.POST['title']
        endDate = request.POST['endDate']
        newElection = Election(electionStatus=True, startDate=date.today(), title=title, numWinners=num_winners, endDate=endDate)
        newElection.save()

    return render(request, 'papsas_app/record/election.html', {
        'electionList': electionList,
        'ongoingElection': ongoingElection,
        'table': table,
        'filter': filter,
    })

@secretary_required
def manage_election(request, id):
    electionList = Election.objects.all()
    ongoingElection = Election.objects.filter(electionStatus=True)

    if request.method == 'POST':
        election = Election.objects.get(id=id)
        election.electionStatus = False
        election.save()
        return redirect('election')
    
    table = ElectionTable(Election.objects.all())
    return render(request, 'papsas_app/record/election.html', {
        'electionList': electionList,
        'ongoingElection': ongoingElection,
        'table': table
    })

@secretary_required
def new_officer(request, num_winners):
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

# @practitioner_required
def vote(request):
    user = request.user
    ongoingElection = Election.objects.get( electionStatus = True )
    attended_event = Attendance.objects.filter( user = user, attended = True ).count()
    # candidates = Candidacy.objects.filter( election = ongoingElection )
    candidates = Candidacy.objects.filter(election=ongoingElection).annotate(vote_count=Count('nominee'))
    print(candidates)

    try:
        has_declared = Candidacy.objects.get( candidate = user , election = ongoingElection )
    except:
        has_declared = None

    if request.POST:
        selected_candidates = request.POST.getlist('candidates')

        if not selected_candidates:
            return HttpResponse("No candidate selected." , status=400)
        try:
            user_voted = Vote.objects.filter( voterID = user, election = ongoingElection)
        except Vote.DoesNotExist:
            user_voted = None
        if user_voted:
            messages.error(request, 'You already voted for this election.')
            return render(request, 'papsas_app/form/vote.html', {
                'attended_event' : attended_event,  
                'has_declared' : has_declared
            })

        vote = Vote.objects.create(voterID=user, election = ongoingElection)
        num_selected = len(selected_candidates)
        req_selected = ongoingElection.numWinners
        if num_selected <= req_selected:
            for candidate_id in selected_candidates:
                try:
                    candidate_obj = Candidacy.objects.get(id = candidate_id, election = ongoingElection)
                    vote.candidateID.add(candidate_obj)
                    messages.success(request, 'You have voted successfully.')
                except Candidacy.DoesNotExist:
                    return HttpResponse("Invalid candidate.", status=400)
        elif num_selected == 0:
            messages.error(request, 'Please select a candidate.')
            return redirect('vote')
        else:
            messages.error(request, 'You voted above the limit.')
            return redirect('vote')
        
        return redirect('vote')
    else:
        return render(request, 'papsas_app/form/vote.html', {
            'candidates' : candidates,
            'attended_event' : attended_event,
            'ongoingElection' : ongoingElection,
            'votes' : Vote.objects.filter( voterID = user, election = ongoingElection),
            'user' : request.user,
            'has_declared' : has_declared
        })

@login_required
def profile(request, id):
    try:
        candidacies = Candidacy.objects.filter( candidate = id )
        attended_event = Attendance.objects.filter( user = id )
        elected_officer = Officer.objects.filter(candidateID__candidate= id)
        user = User.objects.get( id = id)
        updateForm = ProfileUpdateForm(instance=user)
    except Exception as e:
        # subject to change
        return HttpResponse(f"Error - {e}", status=400)
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
        'elected_officers' : elected_officer,
        'updateForm' : updateForm
    })

def change_profile(request):
    user = request.user
    if request.method =='POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            response = HttpResponse()
            response['HX-Refresh'] = 'true' 
            return response
    profile(request, user.id)
        
# compose_event
@officer_required
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

            messages.success(request, 'Event posted successfully.')
            
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('event_table')
                return response
            
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
                '[Name]\n'  # Replace with actual sender's name
                '[PAPSAS INC.]\n'
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


            return redirect('event_table')
    else:
        form = EventForm
    return render(request, 'papsas_app/event_management.html', {'form': form})

@login_required
def attendance_form(request, event_id):
    try:
        # Get the event from the event_id in the URL
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound('Event not found')

    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            user = request.user

            event_registration = EventRegistration.objects.filter(user=user, event=event)
            if event_registration.exists():
                attendance, created = Attendance.objects.get_or_create(user=user, event=event_registration.first())
                attendance.attended = form.cleaned_data['attended']
                attendance.save()
                return redirect('index')
            else:
                error_message = 'You are not registered for this event.'
        else:
            error_message = 'Invalid form submission'

        return render(request, 'papsas_app/form/attendance_form.html', {
            'form': form, 
            'event_id': event_id, 
            'event': event,
            'error_message': error_message})
    else:
        form = AttendanceForm()

    return render(request, 'papsas_app/form/attendance_form.html', {
        'form': form, 
        'event_id': event_id,
        'event': event  })

# register event
@login_required
def event_registration_view(request, event_id):
    user = request.user
    event = get_object_or_404(Event, id=event_id)
    form = EventRegistrationForm(user=request.user, event=event)
    try:
        has_registered = EventRegistration.objects.get( user= user, event = event)
        
    except EventRegistration.DoesNotExist:
        has_registered = None
    except Event.DoesNotExist:
        return HttpResponseNotFound()
    except Exception as e:
        print(f'error: {e}')
        return HttpResponseNotFound()
    
    if request.method == 'POST':
        # Include the user and event in the POST data
        post_data = request.POST.copy()
        post_data['user'] = request.user.id
        post_data['event'] = event.id
        
        form = EventRegistrationForm(
            user=request.user, 
            event=event, 
            data=post_data, 
            files=request.FILES
        )
        if form.is_valid():
            try:
                form.save()  # No need for commit=False here
                messages.success(request, "You have successfully registered for the event.")
                return redirect( 'event_registration_table', event_id = event.id )
            except IntegrityError:
                messages.error(request, "You are already registered for this event.")
            except ValidationError as e:
                messages.error(request, f"Registration failed: {e}")
    else:

        return render(request, 'papsas_app/form/event_registration_form.html', {
            'form': form,
            'event': event,
            'has_registered' : has_registered
        })

def about(request):
    return render(request, 'papsas_app/view/about_us.html')

def become_member(request):
    memType = MembershipTypes.objects.all()
    return render(request, 'papsas_app/view/become_member.html', {
        'memType' : memType
    })

def news_offers(request):
    news_offers = NewsandOffers.objects.all().order_by('-id')

    paginator = Paginator(news_offers, 5)
    page_number = request.GET.get('page')
    news_offers_page = paginator.get_page(page_number)
    
    return render(request, 'papsas_app/view/news_offers.html', {
        'news_offers' : news_offers_page
    })

@secretary_required
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
        return HttpResponseNotFound('Page not Found.')

@secretary_required
def update_account(request, id):
    try:
        user = User.objects.get(id=id)
        form = UserUpdateForm(instance=user)

        if request.method == 'POST':
            form = UserUpdateForm(request.POST, instance=user)
            if form.is_valid():
                region = form.cleaned_data.get('region')
                occupation = form.cleaned_data.get('occupation')
                birthDate = form.cleaned_data.get('birthdate')
                age = form.cleaned_data.get('age')

                if region == 'Region':
                    form.add_error('region', 'Select a valid region.')
                if occupation == 'Occupation':
                    form.add_error('occupation', 'Select a valid occupation.')

                if birthDate:
                    calculated_age = date.today().year - birthDate.year - ((date.today().month, date.today().day) < (birthDate.month, birthDate.day))
                    if age != calculated_age:
                        form.add_error('age', 'Birthdate and Age did not match. Please input the correct details')

                if form.errors:
                    return JsonResponse({'errors': form.errors}, status=400)

                form.save()
                messages.success(request, 'Updated successfully.')
                return redirect('user_record')

            else:
                return JsonResponse({'errors': form.errors}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 

@login_required
def membership_registration(request, mem_id):
    form = MembershipRegistration(request.user, mem_id)
    membership = mem_id

    if request.method == 'POST':
        memType = MembershipTypes.objects.get( id = mem_id )
        form = MembershipRegistration(request.user, mem_id, data=request.POST, files = request.FILES)
        infinite = timedelta(days=36500)
        if form.is_valid():
            user_membership = form.save(commit=False)
            user_membership.user = request.user
            user_membership.membership_type = memType
            user_membership.save()

            if memType.duration is not None:
                user_membership.expirationDate = user_membership.registrationDate + memType.duration
            else:
                user_membership.expirationDate = user_membership.registrationDate + infinite
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

@secretary_required
def membership_record(request):
    record = UserMembership.objects.all()
    if is_officer(request):
        return render(request, 'papsas_app/record/membership_record.html', {
            'record' : record,
        })
    else:
        return redirect('index')
    
@secretary_required 
def approve_membership(request, id): 
    userID = id 
    try:
        if request.method == 'POST': 
            user_membership = UserMembership.objects.get(user=userID) 
            user_membership.status = 'Approved' 
            user_membership.save()

            subject = 'Membership Approved'
            message = f'Dear {user_membership.user.first_name},\n\nYour membership has been approved.\n\nBest regards,\nPASAS INC.'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_membership.user.email])
            messages.success(request, 'Membership approval successful.')
            return redirect('membership_table') 
    except Exception as e: 
        messages.error(request, f'Error: {e}')
        return redirect('membership_table') 

@secretary_required 
def decline_membership(request, id): 
    userID = get_object_or_404( User, id = id )
    try:
        if request.method == 'POST': 
            user_membership = UserMembership.objects.get(user=userID) 
            user_membership.status = 'Declined' 
            user_membership.save()

            subject = 'Membership Declined'
            message = f'Dear {user_membership.user.first_name},\n\nWe regret to inform you that your membership has been declined.\n\nBest regards,\nPAPSAS INC.'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_membership.user.email])
            messages.success(request, 'Successfully declined membership.')
            return redirect('membership_table') 
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('membership_table') 

# not used currently, but can be used in the future
@secretary_required
def delete_membership(request, id):
    try:   
        userID = get_object_or_404(User, user=id)
    except:
        return HttpResponseNotFound()
    
    if request.method == 'POST':
        user_membership = UserMembership.objects.get(user=userID)
        user_membership.status = 'Declined'
        user_membership.save()
        return redirect('membership_table')

@secretary_required
def get_user_info(request, id):
    user = get_object_or_404(User, id = id)
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
    
@member_or_officer_required
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
    form = PasswordResetForm()
    if request.method == 'POST':
        # email = request.POST.get('email')
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)    

            except ObjectDoesNotExist:
                form.add_error('email', 'Enter existing email.')
                return redirect('password_reset')
            except Exception as e:
                print(e)    
                form.add_error('email', e)
                return redirect('password_reset')
            
            if (user.verification_code is None or 
                user.verification_code_expiration is None or 
                timezone.now() > user.verification_code_expiration):
                
                user.verification_code = random.randint(100000, 999999)
                user.verification_code_expiration = timezone.now() + timedelta(minutes=2)
                user.save()

                subject = 'Password Reset Verification Code'
                message = f'Dear {user.first_name},\n\nYour verification code is: {user.verification_code}\n\nPlease enter this code to reset your password.\n\nBest regards,\nPhilippine Association of Practioners of Student Affairs and Services'
                send_mail(subject, message, 'your_email@example.com', [user.email])

            return redirect('password_reset_verify', user_id=user.id)
        else:
            print(form.errors)
            return render(request, 'papsas_app/password_reset.html', {'form': form})  
    else:
        form.fields['email'].widget.attrs['placeholder'] = 'Enter your email address'
        form.fields['email'].widget.attrs['class'] = 'password-reset'
        return render(request, 'papsas_app/password_reset.html', {'form': form})


def password_reset_verify(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        code = (
            request.POST['code-1'] +
            request.POST['code-2'] +
            request.POST['code-3'] +
            request.POST['code-4'] +
            request.POST['code-5'] +
            request.POST['code-6']
        )

        if user.verification_code == int(code):
            return redirect('password_reset_confirm', user_id=user.id)

        if user.verification_code_expiration is None or timezone.now() > user.verification_code_expiration:
            return render(request, 'papsas_app/password_reset_verify.html', {
                'message': 'Verification code has expired. Please request a new one.',
                'resend_code': True,
                'user': user,
                'expiration_timestamp': 0
            })

        return render(request, 'papsas_app/password_reset_verify.html', {
            'message': 'Invalid Verification Code',
            'user': user,
            'resend_code': False,
            'expiration_timestamp': int(user.verification_code_expiration.timestamp())
        })

    if user.verification_code_expiration is None or timezone.now() > user.verification_code_expiration:
        user.verification_code = random.randint(100000, 999999)
        user.verification_code_expiration = timezone.now() + timezone.timedelta(minutes=2)
        user.save()

        subject = 'Password Reset Verification Code'
        message = f'Dear {user.first_name},\n\nYour verification code is: {user.verification_code}\n\nPlease enter this code to reset your password.\n\nBest regards,\nPhilippine Association of Practitioners of Student Affairs and Services'
        send_mail(subject, message, 'your_email@example.com', [user.email])

    return render(request, 'papsas_app/password_reset_verify.html', {
        'user': user,
        'resend_code': False,
        'expiration_timestamp': int(user.verification_code_expiration.timestamp()),
        'message': ''
    })

def password_reset_confirm(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 == password2:
            try:
                # Validate the new password
                validate_password(password1)
                user.set_password(password1)
                user.save()
                return redirect('login')
            except ValidationError as e:
                # Handle validation errors
                return render(request, 'papsas_app/password_reset_confirm.html', {'message': e.messages})
        else:
            return render(request, 'papsas_app/password_reset_confirm.html', {'message': 'Passwords do not match'})
    
    return render(request, 'papsas_app/password_reset_confirm.html', {'user_id': user_id})

def count_vote(id):
    candidate = Candidacy.objects.get(id= id)  # replace with the actual candidate id
    num_votes = candidate.vote_set.count()

    return num_votes

@officer_required
def compose_venue(request):
    form = VenueForm()

    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue posted successfully.')
            
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('venue_table')
                return response
    return render(request, 'papsas_app/form/compose_venue.html', {
        'form': form,
    })

@member_or_officer_required
def event_list(request):
    events = Event.objects.all()

    paginator = Paginator(events, 5) 
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)

    return render(request, 'papsas_app/view/event_view.html', {
        'events': events_page,
    })

# view all event with its attendance and registration records

@secretary_required
def get_receipt(request, user_id):
    user = get_object_or_404(User, id=user_id)
    try:
        user_registration = UserMembership.objects.get(user=user)
        receipt = user_registration.receipt.url
        receipt_data = {
            'receipt': receipt
        }
        return JsonResponse(receipt_data)
    
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'User or UserMembership not found'}, status=404)
    
def get_id(request, user_id):
    user = User.objects.get(User, id=user_id)
    try:
        user_registration = UserMembership.objects.get(user=user)
        id = user_registration.verificationID.url
        id_data = {
            'id': id
        }
        return JsonResponse(id_data)
    
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'User or UserMembership not found'}, status=404)

@secretary_required
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

@officer_required
def compose_achievement(request):
    form = AchievementForm()

    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Achievement posted successfully.')
            
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('achievement_table')
                return response
        else:
            return render(request, 'papsas_app/form/compose_achievement.html', {
                'form' : form,
            })
        
    return render(request, 'papsas_app/form/compose_achievement.html', {
        'form' : form
    })

@officer_required
def compose_news_offer(request):
    form = NewsForm()

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'News & Offers posted successfully.')
            
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('news_offers_table')
                return response
        else:
            return render(request, 'papsas_app/form/compose_news_offers.html', {
                'form' : form,
            })

    return render(request, 'papsas_app/form/compose_news_offers.html', {
        'form' : form
    })

def achievement_view(request):
    achievements = Achievement.objects.all().order_by('-id')
    
    paginator = Paginator(achievements, 5) 
    page_number = request.GET.get('page')  
    achievements_page = paginator.get_page(page_number) 

    return render(request, 'papsas_app/view/achievement_view.html', {
        'achievements': achievements_page,
    })

@officer_required
def venue_record(request):
    venues = Venue.objects.all()
    form = VenueForm()
    return render(request, 'papsas_app/record/venue_record.html', {
        'venues' : venues,
        'form' : form,
    })

@officer_required
def achievement_record(request):
    achievements = Achievement.objects.all()
    form = AchievementForm()
    return render(request, 'papsas_app/record/achievement_record.html', {
        'achievements' : achievements,
        'form' : form,
    })

# update achievement
@officer_required
def get_achievement_data(request, achievement_id):
    try:
        achievement = get_object_or_404( Achievement, id = achievement_id )
        if request.method =="POST":
            form = AchievementForm( request.POST, request.FILES, instance = achievement )
            if form.is_valid():
                form.save()
                messages.success(request, 'Updated Successfully.')
                response = HttpResponse()
                response['HX-Refresh'] = 'true' 
                return response
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

@officer_required
def update_news_offer(request, id):
    news_offer = get_object_or_404(NewsandOffers, id = id)
    try:
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
                messages.success(request, 'Updated Successfully.')
                response = HttpResponse()
                response['HX-Refresh'] = 'true' 
                return response
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

@officer_required
def delete_achievement(request, id):
    try:
        achievement = Achievement.objects.get( id = id )
        achievement.delete()
        messages.success(request, 'Deleted successfully.')
        return redirect('achievement_table')
    except Achievement.DoesNotExist:
        return HttpResponseNotFound('Achievement not found')

    except Exception as e:
        return HttpResponse(f'Error: {e}')

@officer_required
def news_offers_record(request):
    news_offers = NewsandOffers.objects.all()
    form = NewsForm()
    return render(request, 'papsas_app/record/news_offers_record.html', {
        'news_offers' : news_offers,
        'form' : form,
        })

@csrf_exempt
@secretary_required
def delete_account(request, id):
    user = get_object_or_404(User, id=id)
    try:
        if request.method == 'POST':
            print(2)
            user.is_active = False
            user.save()
            messages.success(request, 'Deactivated   user successfully.')  # Add a success message
            return redirect('user_table')  # Redirect to the user table view or appropriate view
    except Exception as e:
        print(1)
        messages.error(request, f'Error: {e}')  # Add an error message
        return redirect('user_table') 

#htmx functions

@secretary_required
def get_event(request, view):
    events = Event.objects.all()
    return render(request, 'papsas_app/partial_list/event_list.html', {
        'events': events,
        'view' : view
        })

@member_required
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
@secretary_required
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

@secretary_required
def admin_dashboard(request):
    return render(request, 'papsas_app/admin_dashboard.html')

@secretary_required
def get_membership_distribution_data(request):
    membership_data = UserMembership.objects.values('membership__type').annotate(total=Count('membership')).order_by('-total')
    
    labels = [item['membership__type'] for item in membership_data]
    values = [item['total'] for item in membership_data]
    
    return JsonResponse({
        'labels': labels,
        'values': values,
    })

@secretary_required
def get_attendance_over_time_data(request):
    data = {"labels": [], "values": []}
    
    attendances = Attendance.objects.filter(attended=True)
    attendances_by_day = attendances.annotate(day=TruncDay('date_attended')).values('day').annotate(count=Count('id')).values_list('day', 'count')
    
    for day, count in attendances_by_day:
        data["labels"].append(day.strftime("%Y-%m-%d"))
        data["values"].append(count)
    
    return JsonResponse(data)

@secretary_required
def get_total_events_count(request):
    total_events = Event.objects.count()
    return JsonResponse({'total_events': total_events})

@secretary_required
def get_total_members_count(request):
    total_members = UserMembership.objects.count()
    return JsonResponse({'count': total_members})

@secretary_required
def get_total_events_count(request):
    count = Event.objects.count() 
    return JsonResponse({'count': count})

@secretary_required
def get_total_revenue(request):
    total_revenue = 0
    events = Event.objects.all()  # Get all events

    for event in events:
        approved_registrations = event.activity.filter(status='Approved')
        registrations_count = approved_registrations.count()  # Count how many approved registrations for each event
        if event.price:  # Ensure the price is not None
            total_revenue += event.price * registrations_count  # Multiply price by number of approved registrations

    return JsonResponse({'total_revenue': total_revenue})

@secretary_required
def get_membership_growth(request):
    today = timezone.now()
    start_year = today.year - 10  # Adjust this to how many years you want to show

    # Count new memberships by year
    growth_data = (
        UserMembership.objects.filter(registrationDate__year__gte=start_year)
        .annotate(year=TruncYear('registrationDate'))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )

    # Prepare the response data
    labels = []
    values = []
    for data in growth_data:
        labels.append(data['year'].year)  # TruncYear provides a date-like object
        values.append(data['count'])

    # Ensure all years in range are included, with 0 if no members
    for year in range(start_year, today.year + 1):
        if year not in labels:
            labels.append(year)
            values.append(0)

    # Sort by year
    sorted_data = sorted(zip(labels, values))
    sorted_labels, sorted_values = zip(*sorted_data)

    return JsonResponse({'labels': list(sorted_labels), 'values': list(sorted_values)})

@secretary_required
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

@secretary_required
def get_event_rating(request):
    event_rating = EventRating.objects.aggregate(average_rating=Avg('rating'))
    return JsonResponse(event_rating, safe=False)

@secretary_required
def get_user_distribution_by_region(request):
    filter_type = request.GET.get('filterType', 'all')

    users_by_region = User.objects.exclude(region__isnull=True).values('region').annotate(total=Count('id')).order_by('-total')

    labels = [region['region'] for region in users_by_region] if users_by_region else []
    values = [region['total'] for region in users_by_region] if users_by_region else []

    top_5 = users_by_region[:5] if users_by_region else []
    least_5 = users_by_region[::-1][:5] if users_by_region else []

    if filter_type == 'top5':
        response_data = {
            'labels': [region['region'] for region in top_5],
            'values': [region['total'] for region in top_5],
        }
    elif filter_type == 'least5':
        response_data = {
            'labels': [region['region'] for region in least_5],
            'values': [region['total'] for region in least_5],
        }
    else:
        response_data = {
            'labels': labels,
            'values': values,
            'top_5_labels': [region['region'] for region in top_5],
            'top_5_values': [region['total'] for region in top_5],
            'least_5_labels': [region['region'] for region in least_5],
            'least_5_values': [region['total'] for region in least_5],
        }

    return JsonResponse(response_data)

@secretary_required
def decline_eventReg(request, id):
    if request.method == "POST":
        eventReg = EventRegistration.objects.get( id = id)
        eventReg.status = 'Declined'
        eventReg.save()
        messages.success(request, 'Registration declined successfully.')
        return redirect(request.META.get('HTTP_REFERER', '/')) 
    return HttpResponseForbidden()

@secretary_required
def approve_eventReg(request, id):
    eventReg = EventRegistration.objects.get( id = id)
    if request.method == "POST":
        eventReg = EventRegistration.objects.get( id = id)
        eventReg.status = 'Approved'
        eventReg.save()
        messages.success(request, 'Registration approved successfully.')
        return redirect(request.META.get('HTTP_REFERER', '/')) 
    return HttpResponseForbidden()

@secretary_required
def delete_eventReg(request, id):
    eventReg = get_object_or_404( EventRegistration, id = id)
    if request.method == "POST":
        eventReg = EventRegistration.objects.get( id = id)
        eventReg.delete()
        messages.success(request, 'Registration deleted successfully.')
        return redirect(request.META.get('HTTP_REFERER', '/')) 
    return HttpResponseForbidden()

@secretary_required
def delete_news_offer(request, id):
    news_offer = get_object_or_404(NewsandOffers, id = id)
    try:
        news_offer.delete()
        messages.success(request, 'Deleted successfully.')
        return redirect('news_offers_table')
    except Exception as e:
        return render(request, 'papsas_app/record/news_offers_table.html', {
            'error': f'Error found: {e}',
        })

@secretary_required
def delete_venue(request, id):
    try:
        venue = get_object_or_404(Venue, id = id)
        if request.method == "POST":
            venue.delete()
            messages.success(request, 'Deleted successfully.')
            return redirect('venue_table')
    except Exception as e:
        return render(request, 'papsas_app/record/venue_table.html', {
            'error': f'Error found: {e}',
            })

@secretary_required
def update_venue(request, id):
    try:
        venue = get_object_or_404(Venue, id = id)
        if request.method == "POST":
            form = VenueForm(request.POST, instance = venue)
            if form.is_valid():
                form.save()
                messages.success(request, 'Updated successfully.')
                response = HttpResponse()
                response['HX-Refresh'] = 'true' 
                return response
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

@secretary_required
def delete_event (request, id):
    try:
        event = Event.objects.get(id = id)
        if request.method == "POST":
            event.delete()
            messages.success(request, 'Deleted successfully.')
            return redirect('event_table')

    except Exception as e:
        return render(request, 'papsas_app/record/event_table.html', {
            'error': f'Error found: {e}',
            })

@secretary_required
def update_event (request, id):
    try:
        event = get_object_or_404(Event, id = id)
        if request.method == "POST":
            form = EventForm(request.POST, request.FILES, instance = event)
            if form.is_valid:
                form.save()
                print('update event')
                messages.success(request, 'Updated successfully.')
                response = HttpResponse()
                response['HX-Refresh'] = 'true'
                return response
            else:
                return render(request, 'papsas_app/record/event_table.html', {
                    'error': 'Invalid form data.',
                    'form': form,
                    })
        data = {
            'name' : event.eventName,
            'startDate': event.startDate,
            'endDate': event.endDate,
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
        return render(request, 'papsas_app/record/event_table.html', {
            'error': f'Error found: {e}',
            })

#JS fetching
@secretary_required
def get_attendees(request, event_id):
    try:
        eventId = get_object_or_404(Event, id=event_id)
        attendances = Attendance.objects.filter(event__event_id=eventId)
        attendees = []
        for attendance in attendances:
            attendees.append({
                'username': attendance.user.username,
                'first_name': attendance.user.first_name,
                'last_name': attendance.user.last_name,
                'status' : attendance.attended
            })
            return JsonResponse(attendees, safe=False)
    except Event.DoesNotExist:
        return HttpResponseNotFound()

def get_event_details(request, id):
    try:
        event = get_object_or_404(Event, id = id)
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
    except Event.DoesNotExist:
        return HttpResponseNotFound()

@method_decorator(secretary_required, name='dispatch')
class UserListView(SingleTableView):
    model = User
    table_class = UserTable
    template_name = 'papsas_app/record/user_record.html'
    filterset_class = UserFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table
    
    def get_queryset(self):
        queryset = User.objects.all()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        paginator = context['paginator']
        page_obj = context.get('page_obj')

        context['form'] = UserUpdateForm()

        if page_obj is not None:
            page_number = page_obj.number
            page_range = paginator.page_range

            start_index = page_number - 2 if page_number > 2 else 1
            end_index = page_number + 2 if page_number < paginator.num_pages - 1 else paginator.num_pages

            page_range = page_range[start_index:end_index]

            context['page_range'] = page_range
            context['page_number'] = page_number
        else:
            context['page_range'] = []
            context['page_number'] = None

        return context
    
    def post(self, request, *args, **kwargs):
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            form = UserUpdateForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'User updated successfully.')
                return redirect(reverse('user_table'))
            else:
                messages.error(request, 'Error updating user. Please check the form.')
                return self.get(request, *args, **kwargs)
    
@method_decorator(secretary_required, name='dispatch')
class MembershipListView(SingleTableView):
    model = UserMembership
    table_class = MembershipTable
    template_name = 'papsas_app/record/membership_table.html'
    filterset_class = MembershipFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        queryset = UserMembership.objects.all()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super(MembershipListView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context
    
@method_decorator(member_required, name='dispatch')
class UserMembershipListView(SingleTableView):
    model = UserMembership
    table_class = UserMembershipTable
    template_name = 'papsas_app/record/single_membership_table.html'
    filterset_class = MembershipFilter
    paginator_class = LazyPaginator

    def get_queryset(self):
        queryset = UserMembership.objects.filter(user=self.request.user)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super(UserMembershipListView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context
    
@method_decorator(secretary_required, name='dispatch')
class EventListView(SingleTableView):
    model = Event
    table_class = EventTable
    template_name = 'papsas_app/record/event_table.html'
    filterset_class = EventFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        queryset = Event.objects.all()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context['form'] = EventForm()
        context['filter'] = self.filterset
        return context
    
    def post(self, request, *args, **kwargs):
            event_id = request.POST.get('event_id')
            event = get_object_or_404(User, id=event_id)
            form = EventForm(request.POST, request.FILES, instance=event)
            if form.is_valid():
                form.save()
                messages.success(request, 'Event updated successfully.')
                return redirect(reverse('event_table'))
            else:
                messages.error(request, 'Error updating user. Please check the form.')
                return self.get(request, *args, **kwargs)
            
@method_decorator(member_required, name='dispatch')
class EventRegistrationListView(SingleTableView):
    model = EventRegistration
    table_class = EventRegistrationTable
    template_name = 'papsas_app/record/event_registration_table.html'
    filterset_class = EventRegistrationFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        queryset = EventRegistration.objects.filter(event_id=event_id)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super(EventRegistrationListView, self).get_context_data(**kwargs)
        event = Event.objects.get(id = self.kwargs.get('event_id'))
        context['name'] = event.eventName
        context['filter'] = self.filterset
        context['event_id'] = self.kwargs.get('event_id')
        return context

@method_decorator(member_required, name='dispatch')
class UserEventRegistrationListView(SingleTableView):
    model = EventRegistration
    table_class = UserEventRegistrationTable
    template_name = 'papsas_app/record/user_event_registration_table.html'
    filterset_class = EventRegistrationFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        queryset = EventRegistration.objects.filter( user = self.request.user )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super(UserEventRegistrationListView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context
    
@method_decorator(secretary_required, name='dispatch')
class EventAttendanceListView(SingleTableView):
    model = Attendance
    table_class = EventAttendanceTable
    template_name= 'papsas_app/record/event_attendance_table.html'
    filterset_class = AttendanceFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        queryset = Attendance.objects.filter(event__event_id=event_id)
        print(queryset)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super(EventAttendanceListView, self).get_context_data(**kwargs)
        event = Event.objects.get(id = self.kwargs.get('event_id'))
        context['name'] = event.eventName
        context['filter'] = self.filterset
        context['event_id'] = self.kwargs.get('event_id')
        return context
    
@method_decorator(member_required, name='dispatch')
class UserEventAttendanceListView(SingleTableView):
    model = Attendance
    table_class = UserEventAttendanceTable
    template_name= 'papsas_app/record/user_event_attendance_table.html'
    filterset_class = AttendanceFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        queryset = Attendance.objects.filter( user = self.request.user )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super(UserEventAttendanceListView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

@method_decorator(officer_required, name='dispatch')
class VenueListView(SingleTableView):
    model = Venue
    table_class = VenueTable
    template_name = 'papsas_app/record/venue_table.html'
    filterset_class = VenueFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        queryset = Venue.objects.all()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super(VenueListView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['form'] = VenueForm
        return context

@method_decorator(officer_required, name='dispatch')
class AchievementListView(SingleTableView):
    model = Achievement
    table_class = AchievementTable
    template_name = 'papsas_app/record/achievement_table.html'
    filterset_class = AchievementFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        queryset = Achievement.objects.all()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super(AchievementListView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['form'] = AchievementForm
        return context
    
@method_decorator(officer_required, name='dispatch')
class NewsAndOffersListView(SingleTableView):
    model = NewsandOffers
    table_class = NewsAndOfferTable
    template_name = 'papsas_app/record/news_offers_table.html'
    filterset_class = NewsAndOfferFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        queryset = NewsandOffers.objects.all()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super(NewsAndOffersListView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['form'] = NewsForm
        return context

def get_expiring_memberships():
    today = timezone.now().date()
    three_days_from_now = timezone.now().date() + timedelta(days=3)
    expiring_memberships = UserMembership.objects.filter(
        expirationDate__gt = today,
        expirationDate__lte = three_days_from_now
        )
    return expiring_memberships

def generate_qr(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    attendance_url = reverse('attendance_form', args=[event.id])
    full_url = f"http://{settings.SITE_DOMAIN}{attendance_url}"

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(full_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="event_{event.id}_qr.png"'

    return response

@method_decorator(secretary_required, name='dispatch')
class ElectionListView(SingleTableView):
    model = Candidacy
    table_class = VoteTable
    template_name = 'papsas_app/record/election_table.html'
    filterset_class = CandidateFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request,
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10,
            }
        ).configure(table)
        return table

    def get_queryset(self):
        election_id = self.kwargs.get('election_id')
        # Annotate vote counts for each candidacy
        queryset = (
            Candidacy.objects.filter(election=election_id)
            .annotate(vote_count=Count('nominee'))
            .select_related('candidate', 'election')
        )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['electionId'] = self.kwargs.get('election_id')
        return context

def upload_tor(request, id):
    user = request.user
    if request.method =='POST':
        # save the image as profilePic from 
        form = TORForm(request.POST, request.FILES)
        if form.is_valid():
            tor = form.cleaned_data['tor']
            user.tor = tor
            user.save()
            return redirect('profile', id = id)
        
def declare_candidacy(request, id):
    user = request.user
    election = Election.objects.get( id = id )
    attended_event = Attendance.objects.filter( user = user, attended = True ).count()
    if request.method == 'POST':
        if attended_event >= 2 and user.tor:
            # Create a new Candidacy record
            candidacy = Candidacy(
                candidate=user,
                election=election
            )
            candidacy.save()
            messages.success(request, 'Candidacy submitted successfully.')
            return redirect('vote')
        else:
            messages.error(request, 'You must attend at least 2 events and have your TOR to declare your candidacy.')

def box_plot(request, event_id = None):
    if event_id:
        event = Event.objects.get(id=event_id)
    else:
        event = Event.objects.filter(date__lt=date.today()).latest('startDate')[:3]
        print(event)
    feedbacks = event.ratings.all()

    ratings = [ feedback.rating for feedback in feedbacks ]

    data = {
        'event': {
            'id': event.id,
            'name': event.eventName,
        },
        'ratings': ratings
    }

    return JsonResponse (data)

def box_event (request):
    events = Event.objects.all().order_by('startDate')
    data = [{'id': event.id, 'name': event.eventName} for event in events]
    return JsonResponse(data, safe=False)

@secretary_required
def get_event_price_vs_attendance_data(request):
    events_data = (
        EventRegistration.objects
        .values('event__price')
        .annotate(attendance_count=Count('attendance'))
    )

    data = list(events_data)
    return JsonResponse({'values': data})

@method_decorator(secretary_required, name='dispatch')
class FeedbackListView(SingleTableView):
    model = EventRating
    table_class = FeedbackTable
    template_name = 'papsas_app/record/feedback_table.html'
    filterset_class = FeedbackFilter
    paginator_class = LazyPaginator

    def get_table(self):
        table = super().get_table()
        RequestConfig(
            self.request, 
            paginate={
                "paginator_class": LazyPaginator,
                "per_page": 10
            }
        ).configure(table)
        return table

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        queryset = EventRating.objects.filter( event = event_id )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super(FeedbackListView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['event'] = self.kwargs.get('event_id')
        return context
