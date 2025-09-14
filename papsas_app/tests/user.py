#  Create 1000 dummy account
import random
from django.utils import timezone
from datetime import timedelta
from faker import Faker
from papsas_app.models import User  # Make sure to replace 'myapp' with your actual app name

# List of institutions
institutions = [
    'University of the Philippines Diliman', 'Ateneo de Manila University', 'De La Salle University', 
    'University of Santo Tomas', 'Mapua University', 'Polytechnic University of the Philippines', 
    'Far Eastern University', 'University of the Philippines Los Baños', 'University of the Philippines Visayas', 
    'Mindanao State University', 'Cebu Normal University', 'Pampanga Agricultural College', 'Bicol University', 
    'Western Mindanao State University', 'Technological University of the Philippines', 
    'Lyceum of the Philippines University', 'Batangas State University', 'Central Philippine University', 
    'Silliman University', 'Xavier University', 'University of San Carlos', 'Pamantasan ng Lungsod ng Maynila','Batangas State University'
]

# List of regions
Regions = [
    ('Region', 'Region'),
    ('National Capital Region', 'NCR'),
    ('Cordillera Administrative Region', 'CAR'),
    ('Ilocos Region', 'Region I'),
    ('Cagayan Valley', 'Region II'),
    ('Central Luzon', 'Region III'),
    ('Calabarzon', 'Region IV-A'),
    ('Mimaropa', 'Region IV-B'),
    ('Bicol Region', 'Region V'),
    ('Western Visayas', 'Region VI'),
    ('Central Visayas', 'Region VII'),
    ('Eastern Visayas', 'Region VIII'),
    ('Zamboanga Peninsula', 'Region IX'),
    ('Northern Mindanao', 'Region X'),
    ('Davao Region', 'Region XI'),
    ('Soccsksargen', 'Region XII'),
    ('Caraga', 'Region XIII'),
    ('Bangsamoro Autonomous Region in Muslim Mindanao', 'BARMM')
]

# Initialize Faker
fake = Faker('fil_PH')

# Create 1000 dummy users
for _ in range(1000):
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    # Email and username based on first and last name
    email = f"{first_name.lower()}{last_name.lower()}@gmail.com"
    username = email
    
    # Mobile number in Philippine format (e.g. 09171234567)
    mobile_number = f"09{random.randint(100000000, 999999999)}"
    
    # Random age between 18 and 65
    age = random.randint(18, 65)
    
    # Determine occupation based on age
    occupation = 'Student' if age <= 22 else 'Practitioner'
    
    # Random institution from the list
    institution = random.choice(institutions)
    
    # Random region from the list
    region = random.choice(Regions)[0]  # Select the name of the region
    
    # Randomly set email_verified to True or False
    email_verified = random.choice([True, False])
    
    # Create user instance
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
        mobileNum=mobile_number,
        region=region,  # Set the random region
        address=fake.address(),
        occupation=occupation,
        age=age,
        birthdate=fake.date_of_birth(minimum_age=age, maximum_age=age),
        institution=institution,
        verification_code=None,  # No verification code
        verification_code_expiration=None,  # No expiration
        email_verified=email_verified,  # Set random email_verified
    )
    
    # Set the password to 'Papsas_123'
    user.set_password('Papsas_123')
    
    # Save the user to the database
    user.save()

print("1000 dummy users created successfully.")

# Get all that user to feed to gpt
from papsas_app.models import User
users = User.objects.all()
for user in users:
    print(user)

# Get all the membership to feed to gpt
from papsas_app.models import MembershipTypes
memberships = MembershipTypes.objects.all()
for membership in memberships:
    print(membership)

# Make dummy registrations
from papsas_app.models import User, UserMembership, MembershipTypes
import random
from datetime import timedelta, date
from faker import Faker
fake=Faker()
membership_types = {
    1: {'type': 'Regular', 'duration': 1},  # Duration in years
    2: {'type': 'Special', 'duration': 2},
    3: {'type': 'Affiliate', 'duration': 2},
    4: {'type': 'Lifetime', 'duration': 100}
}
status_choices = ['Approved', 'Declined']
users = User.objects.filter(id__gte=47, id__lte=1441, email_verified = True)
membership_regular = MembershipTypes.objects.get(type="Regular")
membership_special = MembershipTypes.objects.get(type="Special")
membership_affiliate = MembershipTypes.objects.get(type="Affiliate")
membership_lifetime = MembershipTypes.objects.get(type="Lifetime")
for user in users:
    last_membership = UserMembership.objects.filter(user=user).last()
    if last_membership and last_membership.expirationDate > date.today():
        continue
    membership_id = random.choice(list(membership_types.keys()))
    membership_type = membership_types[membership_id]
    membership = None
    if membership_id == 1:
        membership = membership_regular
    elif membership_id == 2:
        membership = membership_special
    elif membership_id == 3:
        membership = membership_affiliate
    elif membership_id == 4:
        membership = membership_lifetime
    registration_date = fake.date_this_decade(before_today=True, after_today=False)
    expiration_date = registration_date + timedelta(days=365 * membership_type['duration'])
    receipt = 'papsas_app/reciept/receipt.png'
    verificationID = 'papsas_app/verificationID/valid_id.jpg'
    reference_number = random.randint(100000, 999999)
    status = random.choice(status_choices)
    user_membership = UserMembership(
        user=user,
        membership=membership,
        registrationDate=registration_date,
        expirationDate=expiration_date,
        reference_number=reference_number,
        status=status
    )
    user_membership.save()

print("User memberships created successfully.")

# Get all events
from papsas_app.models import Event
events = Event.objects.all()
for event in events:
    print(event)

# Create them Registration records
from papsas_app.models import User, Event, EventRegistration
import random
from faker import Faker
from datetime import datetime
fake = Faker()
events = Event.objects.all()
status_choices = ['Approved', 'Declined']
receipt_path = 'papsas_app/reciept/receipt.png'
users = User.objects.filter(id__gte=1, id__lte=1441)
total_registrations = 0
for _ in range(1000):
    event = random.choice(events)
    if event.exclusive:
        eligible_users = users.filter(occupation='Practitioner')
    else:
        eligible_users = users
    if eligible_users.exists():
        user = random.choice(eligible_users)
        reference_number = random.randint(100000, 999999)
        registration_status = random.choice(status_choices)
        start_date = event.startDate
        one_month_before = start_date - timedelta(days=30)
        registered_at = fake.date_time_between(start_date=one_month_before, end_date=start_date)
        registration = EventRegistration(
            user=user,
            event=event,
            receipt=receipt_path,
            reference_number=reference_number,
            registered_at=registered_at,
            status=registration_status
        )
        registration.save()
        total_registrations += 1
print(f"{total_registrations} EventRegistration records created successfully.")



from papsas_app.models import Attendance, EventRegistration, Event
from faker import Faker
import random
from datetime import timedelta
fake = Faker()
provinces = [
    "Metro Manila", "Cebu", "Davao", "Iloilo", "Laguna", "Pampanga", 
    "Batangas", "Rizal", "Cagayan", "Bataan", "Zamboanga", "Palawan"
]
approved_registrations = EventRegistration.objects.filter(status='Approved')
total_attendance = 0
for _ in range(6000):
    registration = random.choice(approved_registrations)
    event = registration.event
    start_date = event.startDate
    end_date = event.endDate
    date_attended = fake.date_between(start_date=start_date, end_date=end_date)
    if Attendance.objects.filter(user=registration.user, event=registration, date_attended=date_attended).exists():
        continue 
    next_location = random.choice(provinces + [None])
    attendance = Attendance( user=registration.user, event=registration, attended=True, date_attended=date_attended, next_location=next_location,
    )
    attendance.save()
    total_attendance += 1
print(f"{total_attendance} Attendance records created successfully.")

from papsas_app.models import User, Event, EventRegistration, EventRating
import random
from faker import Faker
from datetime import timedelta
fake = Faker()
registrations = EventRegistration.objects.filter(status="Approved")
total_ratings = 0
for _ in range(500):
    registration = random.choice(registrations)
    if EventRating.objects.filter(event=registration.event, user=registration.user).exists():
        continue
    rating = random.randint(3, 5)
    comment = fake.sentence(nb_words=10) if random.choice([True, False]) else None
    end_date = registration.event.endDate
    created_at = fake.date_time_between(start_date=end_date + timedelta(days=1), end_date=end_date + timedelta(days=30))
    updated_at = created_at
    event_rating = EventRating(
        event=registration.event,
        user=registration.user,
        rating=rating,
        comment=comment,
        created_at=created_at,
        updated_at=updated_at,
    )
    event_rating.save()
    total_ratings += 1
    if total_ratings >= 500:
        break
print(f"{total_ratings} EventRating records created successfully.")

# Create a record for each event
from papsas_app.models import User, Event, EventRegistration
import random
from faker import Faker
from datetime import timedelta
fake = Faker()
events = Event.objects.all()
status_choices = ['Approved']
receipt_path = 'papsas_app/reciept/receipt.png'
users = User.objects.filter(id__gte=1, id__lte=1441)
total_registrations = 0
for event in events:
    if event.exclusive:
        eligible_users = users.filter(occupation='Practitioner')
    else:
        eligible_users = users
    for user in eligible_users:
        reference_number = random.randint(100000, 999999)
        registration_status = random.choice(status_choices)
        start_date = event.startDate
        one_month_before = start_date - timedelta(days=30)
        registered_at = fake.date_time_between(start_date=one_month_before, end_date=start_date)
        registration = EventRegistration(
            user=user,
            event=event,
            receipt=receipt_path,
            reference_number=reference_number,
            registered_at=registered_at,
            status=registration_status
        )
        registration.save()
        total_registrations += 1
print(f"{total_registrations} EventRegistration records created successfully.")
