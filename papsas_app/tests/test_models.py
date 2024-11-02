from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from papsas_app.models import User, MembershipTypes, UserMembership, Election, Candidacy, Vote, Officer, Venue, Event, EventRating, Achievement, NewsandOffers, EventRegistration, Attendance
import datetime

class TestUser(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            mobileNum="12345678901",
            region="Region",
            address="Test Address",
            occupation="Occupation",
            age=25,
            birthdate=datetime.date(1998, 1, 1),
        )

    def test_user_creation(self):
        """Test if user is created correctly"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.mobileNum, "12345678901")
        self.assertEqual(self.user.age, 25)

    def test_mobile_number_validation(self):
        """Test mobile number validation"""
        # Test invalid mobile number
        user = User(
            username="test2",
            password="test123",
            mobileNum="123"  # Invalid mobile number
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_age_validation(self):
        """Test age validation"""
        # Test age below minimum
        user = User(
            username="test3",
            password="test123",
            mobileNum="12345678901",
            age=15
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

        # Test age above maximum
        user.age = 101
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_verification_code_expiration(self):
        """Test verification code expiration functionality"""
        self.user.verification_code = 123456
        self.user.save()
        
        # Check if expiration time is set
        self.assertIsNotNone(self.user.verification_code_expiration)
        
        # Check if expiration is roughly 2 minutes from now
        time_diff = self.user.verification_code_expiration - timezone.now()
        self.assertTrue(115 <= time_diff.total_seconds() <= 125)  # roughly 2 minutes (120 seconds)

    def test_get_expiration_timestamp(self):
        """Test get_expiration_timestamp method"""
        self.user.verification_code = 123456
        self.user.save()
        
        timestamp = self.user.get_expiration_timestamp()
        self.assertIsNotNone(timestamp)
        self.assertIsInstance(timestamp, int)

    def test_str_method(self):
        """Test string representation of User"""
        expected_str = f'{self.user.id} - {self.user.first_name}'
        self.assertEqual(str(self.user), expected_str)

    def test_password_hashing(self):
        """Test if password is properly hashed"""
        raw_password = "testpass123"
        self.assertNotEqual(self.user.password, raw_password)
        self.assertTrue(self.user.check_password(raw_password))

    def test_profile_pic_default(self):
        """Test default profile picture"""
        self.assertEqual(
            self.user.profilePic.name,
            "papsas_app/images/default_dp.jpeg"
        )

    def test_email_verification_default(self):
        """Test default email verification status"""
        self.assertFalse(self.user.email_verified)

class TestUserMembership(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            mobileNum="12345678901",
            region="Region",
            address="Test Address",
            occupation="Student",
            age=25
        )

        # Create a test membership type
        self.membership_type = MembershipTypes.objects.create(
            type="Regular",
            description="Regular membership",
            duration=timedelta(days=365),  # 1 year
            fee=Decimal('1000.00')
        )

        # Create a test user membership
        self.user_membership = UserMembership.objects.create(
            user=self.user,
            membership=self.membership_type,
            reference_number=123456789,
            status='Pending'
        )

    def test_membership_type_creation(self):
        """Test if membership type is created correctly"""
        self.assertEqual(self.membership_type.type, "Regular")
        self.assertEqual(self.membership_type.fee, Decimal('1000.00'))
        self.assertEqual(self.membership_type.duration, timedelta(days=365))

    def test_user_membership_creation(self):
        """Test if user membership is created correctly"""
        self.assertEqual(self.user_membership.user, self.user)
        self.assertEqual(self.user_membership.membership, self.membership_type)
        self.assertEqual(self.user_membership.status, 'Pending')
        self.assertIsNotNone(self.user_membership.registrationDate)

    def test_user_membership_expiration(self):
        """Test if expiration date is calculated correctly"""
        expected_expiration = self.user_membership.registrationDate + self.membership_type.duration
        self.assertEqual(self.user_membership.expirationDate, expected_expiration)

    def test_user_membership_status_choices(self):
        """Test if status choices are enforced"""
        # Test valid status
        self.user_membership.status = 'Approved'
        self.user_membership.save()
        self.assertEqual(self.user_membership.status, 'Approved')

        # Test invalid status
        with self.assertRaises(Exception):
            self.user_membership.status = 'Invalid'
            self.user_membership.full_clean()

    def test_user_membership_string_representation(self):
        """Test string representation of UserMembership"""
        expected_str = f'{self.user.id} : {self.user.first_name} - {self.user_membership.id} : {self.membership_type}'
        self.assertEqual(str(self.user_membership), expected_str)

    def test_membership_receipt_upload(self):
        """Test receipt upload functionality"""
        # Create a dummy file
        dummy_file = SimpleUploadedFile(
            "test_receipt.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        self.user_membership.receipt = dummy_file
        self.user_membership.save()
        self.assertTrue(self.user_membership.receipt.url.find('test_receipt.jpg'))

    def test_multiple_memberships(self):
        """Test if a user can have multiple memberships"""
        # Create another membership type
        premium_membership = MembershipTypes.objects.create(
            type="Premium",
            description="Premium membership",
            duration=timedelta(days=730),  # 2 years
            fee=Decimal('2000.00')
        )

        # Create another membership for the same user
        second_membership = UserMembership.objects.create(
            user=self.user,
            membership=premium_membership,
            reference_number=987654321,
            status='Pending'
        )

        # Get all memberships for the user
        user_memberships = UserMembership.objects.filter(user=self.user)
        self.assertEqual(user_memberships.count(), 2)

    def test_membership_dates(self):
        """Test membership dates logic"""
        # Test registration date is set automatically
        self.assertIsNotNone(self.user_membership.registrationDate)
        
        # Test expiration date is calculated correctly
        self.assertEqual(
            self.user_membership.expirationDate,
            self.user_membership.registrationDate + self.membership_type.duration
        )

    def test_membership_verification_id(self):
        """Test verification ID upload"""
        dummy_file = SimpleUploadedFile(
            "test_id.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        self.user_membership.verificationID = dummy_file
        self.user_membership.save()
        
        self.assertTrue(self.user_membership.verificationID.name.find('test_id.jpg'))

    def test_membership_status_update(self):
        """Test membership status update"""
        # Test status update from Pending to Approved
        self.assertEqual(self.user_membership.status, 'Pending')
        self.user_membership.status = 'Approved'
        self.user_membership.save()
        self.assertEqual(self.user_membership.status, 'Approved')

        # Test status update to Declined
        self.user_membership.status = 'Declined'
        self.user_membership.save()
        self.assertEqual(self.user_membership.status, 'Declined')

class TestElection(TestCase):
    def setUp(self):
        self.election = Election.objects.create(
            title="Presidential Election 2024",
            startDate=timezone.now().date(),
            endDate=timezone.now().date() + timedelta(days=30),
            electionStatus=True,
            numWinners=1
        )

    def test_election_creation(self):
        self.assertEqual(self.election.title, "Presidential Election 2024")
        self.assertIsNotNone(self.election.startDate)
        self.assertIsNotNone(self.election.endDate)

class TestCandidacy(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.election = Election.objects.create(
            title="Presidential Election 2024",
            startDate=timezone.now().date(),
            endDate=timezone.now().date() + timedelta(days=30),
            electionStatus=True,
            numWinners=1
        )
        self.candidacy = Candidacy.objects.create(
            candidate=self.user,
            election=self.election,
            candidacyStatus=True
        )

    def test_candidacy_creation(self):
        self.assertEqual(self.candidacy.candidate, self.user)
        self.assertEqual(self.candidacy.election, self.election)

class TestVote(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.election = Election.objects.create(
            title="Presidential Election 2024",
            startDate=timezone.now().date(),
            endDate=timezone.now().date() + timedelta(days=30),
            electionStatus=True,
            numWinners=1
        )
        self.candidacy = Candidacy.objects.create(
            candidate=self.user,
            election=self.election,
            candidacyStatus=True
        )
        self.vote = Vote.objects.create(
            voterID=self.user,
            election=self.election
        )
        self.vote.candidateID.add(self.candidacy)

    def test_vote_creation(self):
        self.assertEqual(self.vote.voterID, self.user)
        self.assertEqual(self.vote.election, self.election)
        self.assertIn(self.candidacy, self.vote.candidateID.all())

class TestOfficer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.election = Election.objects.create(
            title="Presidential Election 2024",
            startDate=timezone.now().date(),
            endDate=timezone.now().date() + timedelta(days=30),
            electionStatus=True,
            numWinners=1
        )
        self.candidacy = Candidacy.objects.create(
            candidate=self.user,
            election=self.election,
            candidacyStatus=True
        )
        self.officer = Officer.objects.create(
            candidateID=self.candidacy,
            position='President',
            termStart=timezone.now().date(),
            termEnd=timezone.now().date() + timedelta(days=365)
        )

    def test_officer_creation(self):
        self.assertEqual(self.officer.position, 'President')
        self.assertEqual(self.officer.candidateID.candidate, self.user)

class TestVenue(TestCase):
    def setUp(self):
        self.venue = Venue.objects.create(
            name="Main Hall",
            address="123 Main St",
            capacity=100
        )

    def test_venue_creation(self):
        self.assertEqual(self.venue.name, "Main Hall")
        self.assertEqual(self.venue.capacity, 100)

class TestEvent(TestCase):
    def setUp(self):
        self.venue = Venue.objects.create(
            name="Main Hall",
            address="123 Main St",
            capacity=100
        )
        self.event = Event.objects.create(
            eventName="Annual Gathering",
            exclusive=True,
            startDate=timezone.now().date(),
            endDate=timezone.now().date() + timedelta(days=1),
            venue=self.venue,
            eventDescription="A gathering for all members.",
            eventStatus=True,
            price=Decimal('50.00 ')
        )

    def test_event_creation(self):
        self.assertEqual(self.event.eventName, "Annual Gathering")
        self.assertEqual(self.event.venue, self.venue)

class TestEventRating(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.venue = Venue.objects.create(
            name="Main Hall",
            address="123 Main St",
            capacity=100
        )
        self.event = Event.objects.create(
            eventName="Annual Gathering",
            exclusive=True,
            startDate=timezone.now().date(),
            endDate=timezone.now().date() + timedelta(days=1),
            venue=self.venue,
            eventDescription="A gathering for all members.",
            eventStatus=True,
            price=Decimal('50.00')
        )
        self.event_rating = EventRating.objects.create(
            event=self.event,
            user=self.user,
            rating=4,
            comment="Good event!"
        )

    def test_event_rating_creation(self):
        self.assertEqual(self.event_rating.event, self.event)
        self.assertEqual(self.event_rating.user, self.user)
        self.assertEqual(self.event_rating.rating, 4)

class TestAchievement(TestCase):
    def setUp(self):
        self.achievement = Achievement.objects.create(
            name="Best Member",
            description="Awarded to the most active member.",
            pubmat="papsas_app/pubmat/achievement/best_member.jpg"
        )

    def test_achievement_creation(self):
        self.assertEqual(self.achievement.name, "Best Member")
        self.assertIsNotNone(self.achievement.description)

class TestNewsandOffers(TestCase):
    def setUp(self):
        self.news = NewsandOffers.objects.create(
            name="New Year Offer",
            description="Get 10% off on all events this January!",
            pubmat="papsas_app/pubmat/newsandoffers/new_year_offer.jpg"
        )

    def test_news_creation(self):
        self.assertEqual(self.news.name, "New Year Offer")
        self.assertIsNotNone(self.news.description)

class TestEventRegistration(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.venue = Venue.objects.create(
            name="Main Hall",
            address="123 Main St",
            capacity=100
        )
        self.event = Event.objects.create(
            eventName="Annual Gathering",
            exclusive=True,
            startDate=timezone.now().date(),
            endDate=timezone.now().date() + timedelta(days=1),
            venue=self.venue,
            eventDescription="A gathering for all members.",
            eventStatus=True,
            price=Decimal('50.00')
        )
        self.event_registration = EventRegistration.objects.create(
            user=self.user,
            event=self.event,
            receipt="papsas_app/reciept/event_registration.jpg",
            reference_number=123456,
            status="Approved"
        )

    def test_event_registration_creation(self):
        self.assertEqual(self.event_registration.user, self.user)
        self.assertEqual(self.event_registration.event, self.event)

class TestAttendance(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.venue = Venue.objects.create(
            name="Main Hall",
            address="123 Main St",
            capacity=100
        )
        self.event = Event.objects.create(
            eventName="Annual Gathering",
            exclusive=True,
            startDate=timezone.now().date(),
            endDate=timezone.now().date() + timedelta(days=1),
            venue=self.venue,
            eventDescription="A gathering for all members.",
            eventStatus=True,
            price=Decimal('50.00')
        )
        self.event_registration = EventRegistration.objects.create(
            user=self.user,
            event=self.event,
            receipt="papsas_app/reciept/event_registration.jpg",
            reference_number=123456,
            status="Approved"
        )
        self.attendance = Attendance.objects.create(
            user=self.user,
            event=self.event_registration,
            attended=True
        )

    def test_attendance_creation(self):
        self.assertEqual(self.attendance.user, self.user)
        self.assertEqual(self.attendance.event, self.event_registration)
        self.assertTrue(self.attendance.attended)