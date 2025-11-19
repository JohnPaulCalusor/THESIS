from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg, Q, UniqueConstraint
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django import forms
from django.utils import timezone
from django.utils.text import slugify
from datetime import date, timedelta
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

# Create your models here.

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

occupation = [
    ('Student', 'Student'),
    ('Practitioner', 'Practitioner'),
]

status = [
    ('Approved', 'Approved'),
    ('Pending', 'Pending'),
    ('Declined', 'Declined')
]

provinces = [
    ('aklan', 'Aklan'),
    ('palawan', 'Palawan'),
    ('benguet', 'Benguet'),
    ('pangasinan', 'Pangasinan'),
    ('metro_manila', 'Metro Manila'),
    ('cebu', 'Cebu'),
    ('davao_del_sur', 'Davao del Sur'),
    ('pampanga', 'Pampanga'),
    ('iloilo', 'Iloilo'),
    ('negros_occidental', 'Negros Occidental'),
    ('zambales', 'Zambales'),
    ('cavite', 'Cavite'),
    ('ilocos_sur', 'Ilocos Sur'),
    ('la_union', 'La Union'),
    ('batangas', 'Batangas'),
    ('camiguin', 'Camiguin'),
    ('bohol', 'Bohol'),
    ('misamis_oriental', 'Misamis Oriental'),
    ('albay', 'Albay'),
    ('surigao_del_norte', 'Surigao del Norte')
]

events = [
    ('Interactive Youth Forum', 'Interactive Youth Forum'),
    ('National Convention', 'National Convention'),
    ('National Research Conference', 'National Research Conference'),
    ('Volunteerism Forum', 'Volunteerism Forum')
]



class User(AbstractUser):
    email = models.EmailField(
        _('email address'),
        unique=True,  # This is important
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    mobileNum = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='Mobile number must be 11 digits.'
            )
        ]
    )
    region = models.CharField(max_length=64, choices=Regions, default='Region',)
    address = models.CharField(max_length=256)
    occupation = models.CharField(max_length=16, choices=occupation, default='Occupation')
    age = models.IntegerField(
        null=True,
        validators=[
            MinValueValidator(18, message="Age must be at least 18."),
            MaxValueValidator(100, message="Age must be less than or equal to 100.")
        ]
    )
    birthdate = models.DateField(null=True, blank=True)
    verification_code = models.IntegerField(null=True, blank=True)
    verification_code_expiration = models.DateTimeField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    profilePic = models.ImageField(null=True, blank=True, upload_to="papsas_app/profilePic", default="papsas_app/images/default_dp.jpeg")
    institution = models.CharField(max_length=128, null=True)
    tor = models.ImageField(upload_to="papsas_app/tor", null=True, blank=True) 


    def get_expiration_timestamp(self):
        return int(self.verification_code_expiration.timestamp()) if self.verification_code_expiration else None

    def __str__(self):
        return f'{self.id} - {self.first_name} - {self.email}'

    def save(self, *args, **kwargs):
        if self.verification_code:
            if not self.verification_code_expiration or timezone.now() > self.verification_code_expiration:
                self.verification_code_expiration = timezone.now() + timezone.timedelta(minutes=2)
        else:
            self.verification_code = None
            self.verification_code_expiration = None
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['id']


class UserSecurity(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security",
    )
    email_verified_at = models.DateTimeField(blank=True, null=True)
    otp_hash = models.CharField(max_length=128, blank=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.PositiveSmallIntegerField(default=0)
    otp_locked_until = models.DateTimeField(blank=True, null=True)
    otp_last_sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "user security guard"
        verbose_name_plural = "user security guards"
        ordering = ["user_id"]

    def is_locked(self):
        return bool(self.otp_locked_until and timezone.now() < self.otp_locked_until)

    def clear_otp_state(self, *, update_fields=None):
        self.otp_hash = ""
        self.otp_expires_at = None
        self.otp_attempts = 0
        self.otp_locked_until = None
        self.otp_last_sent_at = None
        self.save(
            update_fields=update_fields
            or [
                "otp_hash",
                "otp_expires_at",
                "otp_attempts",
                "otp_locked_until",
                "otp_last_sent_at",
            ]
        )


class MembershipTypes(models.Model):
    pubmat = models.ImageField(upload_to="papsas_app/pubmat/event", null=False)
    type = models.CharField(max_length=16, null=True)
    description = models.CharField(max_length=512, null=True)
    duration = models.DurationField(null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.id} - {self.type}'
    
    class Meta:
        ordering = ['id']
    
class UserMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='member')
    membership = models.ForeignKey(MembershipTypes, on_delete=models.CASCADE)
    registrationDate = models.DateField(auto_now_add=True)
    expirationDate = models.DateField(null=True, blank=True)
    receipt = models.ImageField(upload_to="papsas_app/reciept", null=False, blank=False, default="papsas_app/reciept/receipt.png") 
    reference_number = models.BigIntegerField(null=False)
    verificationID = models.ImageField(upload_to="papsas_app/verificationID", null=False, blank=False, default="papsas_app/verificationID/valid_id.jpg") 
    status = models.CharField(max_length=10, choices=status, default='Pending')

    def __str__ (self):
        return f'{self.user.id} : {self.user.first_name} - {self.id} : {self.membership}'

    def save(self, *args, **kwargs):
        if not self.expirationDate:
            self.registrationDate = date.today()
            if self.membership.duration:
                self.expirationDate = self.registrationDate + self.membership.duration
            else:
                self.expirationDate = None  # or some other default value
        super().save(*args, **kwargs)

class Election(models.Model):
    title = models.CharField(max_length=128, null=True)    
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    electionStatus = models.BooleanField()
    numWinners = models.IntegerField(null=True)

    def __str__(self):
        return f'Election {self.id}'
    
    class Meta:
        ordering = ['id']

class Candidacy(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name="candidate")
    candidacyStatus = models.BooleanField(null=True, default=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="elections")
    position = models.ForeignKey(
        'papsas_app.Position',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='candidacies',
    )
    credentials = models.TextField(max_length=9999, null=True)
    
    def __str__(self):
        return f"{self.candidate.first_name} running for Election {self.election.title} {self.election.startDate.year}"
    
    
    # >>> PAPSAS v1.4 BEGIN
    class Meta:
        constraints = [
            # Duplicate candidacy guard when a position is assigned
            UniqueConstraint(
                fields=["election", "position", "candidate"],
                condition=Q(position__isnull=False),
                name="uniq_candidacy_election_pos_member",
            ),
        ]
    # <<< PAPSAS v1.4 END

class Vote(models.Model):
    # LEGACY: candidateID M2M is deprecated; selections now live in VoteChoice.
    # TODO: remove this once VoteChoice is fully populated and consumers stop touching the M2M.
    candidateID = models.ManyToManyField(Candidacy, related_name="nominee")
    voterID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voter")
    voteDate = models.DateField(auto_now_add=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, null=True, related_name="poll")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["voterID", "election"],
                name="unique_vote_per_user_election",
                condition=Q(election__isnull=False),
            ),
        ]
    def __str__(self):
        return f'{self.candidateID.all()}'

    @property
    def selections(self):
        # expose new VoteChoice rows for ease of access
        return self.choices.select_related("candidacy", "position")


class VoteChoice(models.Model):
    """
    Captures one candidacy selection per ballot so we can enforce per-position constraints and aggregate safely.
    """
    vote = models.ForeignKey("Vote", on_delete=models.CASCADE, related_name="choices")
    candidacy = models.ForeignKey("Candidacy", on_delete=models.PROTECT, related_name="vote_choices")
    position = models.ForeignKey("Position", on_delete=models.PROTECT, related_name="vote_choices")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["vote", "candidacy"], name="uq_choice_vote_candidacy"),
        ]

    def clean(self):
        candidacy = getattr(self, "candidacy", None)
        candidacy_position_id = getattr(candidacy, "position_id", None)
        if candidacy_position_id is None and self.candidacy_id:
            candidacy_position_id = (
                Candidacy.objects.filter(id=self.candidacy_id)
                .values_list("position_id", flat=True)
                .first()
            )
        if candidacy_position_id is None:
            return
        if not self.position_id:
            self.position_id = candidacy_position_id
            return
        if self.position_id != candidacy_position_id:
            raise ValidationError("position must equal candidacy.position")

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"VoteChoice(vote={self.vote_id}, candidacy={self.candidacy_id}, position={self.position_id})"


class Officer(models.Model):
    candidateID = models.ForeignKey(Candidacy, on_delete=models.CASCADE, related_name="officers")
    position = models.CharField(max_length=32, choices=[
        ('President', 'President'),
        ('Secretary', 'Secretary'),
        ('Regular', 'Regular')
    ], null=True)
    termStart = models.DateField(null=True)
    termEnd = models.DateField(null=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['candidateID'], name='unique_officer_per_candidacy'),
        ]

    def __str__(self):
        return f"{self.candidateID.candidate.first_name} was elected ({self.termStart} - {self.termEnd})"

class Venue(models.Model):
    name = models.CharField(max_length=64, null=True)
    address = models.CharField(max_length=64, null=True)
    capacity = models.IntegerField()

    def __str__(self):
        return f'{self.name}'


class Event(models.Model):
    eventName = models.CharField(max_length=255, choices=events, null=True)
    exclusive = models.BooleanField(default=True)
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, null=True)
    eventDescription = models.TextField(max_length=9999, null=True)
    eventStatus = models.BooleanField(default=True)
    pubmat = models.ImageField(upload_to="papsas_app/pubmat/event", null=False)
    cover_image = models.ImageField(upload_to="events/", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    startTime = models.TimeField(null=True)
    endTime = models.TimeField(null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    postStamp = models.DateTimeField(auto_now_add=True, null=True)  # date na pinost
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events_created",
    )

    def __str__(self):
        date_year = self.startDate.year if self.startDate else "n/a"
        return f"{self.id} - {self.eventName} {date_year} - Date : {self.startDate} to {self.endDate} - {self.exclusive}"
    
    def short_description(self):
        text = (self.eventDescription or "").strip()
        if len(text) > 100:
            return f'{text[:100]}...'
        return text
    
    def average_rating(self):
        return self.ratings.aggregate(Avg('rating'))['rating__avg']

    def _generate_slug(self):
        base = slugify(self.eventName or "event")
        if not base:
            base = "event"
        candidate = base
        counter = 1
        Klass = self.__class__
        while Klass.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
            counter += 1
            candidate = f"{base}-{counter}"
        return candidate

    def save(self, *args, **kwargs):
        if self.endDate and self.startDate and self.endDate < self.startDate:
            raise ValueError("The end date cannot be less than start Date.")
        if not self.slug:
            self.slug = self._generate_slug()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-startDate']
    
class EventRating(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add= True, null=True)
    updated_at = models.DateTimeField(auto_now_add= True, null=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username}'s rating for {self.event.eventName}"


class EventSignup(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="signup_records",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_signups",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["event", "user"], name="unique_event_signup"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"EventSignup(event={self.event_id}, user={self.user_id})"

class Achievement(models.Model):
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(max_length=9999, null=True)
    postStamp = models.DateTimeField(auto_now_add=True)
    pubmat = models.ImageField(upload_to="papsas_app/pubmat/achievement", null=False)

    def __str__(self):
        return f'{self.id} - {self.name}'
    
    def short_description(self):
        if len(self.description) > 100:
            return f'{self.description[:100]}...'
        return self.description

    class Meta:
        ordering = ['id']
        
class NewsandOffers(models.Model):
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(max_length=9999, null=True)
    postStamp = models.DateTimeField(auto_now_add=True, null=True)
    pubmat = models.ImageField(upload_to="papsas_app/pubmat/newsandoffers", null=False)

    def short_description(self):
        if len(self.description) > 100:
            return f'{self.description[:100]}...'
        return self.description

    class Meta:
        ordering = ['id']
    
class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="activity")
    receipt = models.ImageField(upload_to="papsas_app/reciept", null=False) 
    reference_number = models.IntegerField(null = False)
    registered_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=10, choices=status, default='Pending')

    def __str__(self):
        return f"{self.id} : {self.user.id} : {self.user.username} - {self.event.eventName} at {self.event.venue}"

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audience')
    event = models.ForeignKey(EventRegistration, on_delete=models.CASCADE, related_name='attendance')
    attended = models.BooleanField(default=False)
    date_attended = models.DateField(auto_now_add=True, null=True)
    next_location = models.CharField(choices=provinces, max_length=128, null= True, blank=True)

    class Meta:
        unique_together = ('user', 'event', 'date_attended')

    def __str__(self):
        return f"{self.user.first_name} attended {self.event.event.eventName} at {self.date_attended}"

    


class VisitorStats(models.Model):
    total_visitors = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Total Visitors: {self.total_visitors}"
    
class PageVisit(models.Model):
    key = models.CharField(max_length=100, unique=True)  # e.g. "regional-chapters/region-i"
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.key}: {self.count}"

    class Meta:
        ordering = ["key"]


class RegionalChapterFeedback(models.Model):
    slug = models.CharField(max_length=64, unique=True)  # e.g. "region-i"
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.slug}: 👍 {self.likes} / 👎 {self.dislikes}"

    class Meta:
        ordering = ["slug"]


class VoteSelection(models.Model):
    vote = models.OneToOneField('papsas_app.Vote', on_delete=models.CASCADE, related_name='selection')
    candidate = models.ForeignKey('papsas_app.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"VoteSelection(vote_id={self.vote_id}, candidate_id={self.candidate_id})"

# Ensure Position model module is imported so Django registers it
from .models_position import Position  # noqa: E402,F401
