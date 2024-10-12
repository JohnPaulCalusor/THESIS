from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from ...models import UserMembership
from ...views import get_expiring_memberships

class Command(BaseCommand):
    help = 'Check for memberships expiring in 3 days and send notifications'

    def handle(self, *args, **options):
        expiring_memberships = get_expiring_memberships()
        
        for membership in expiring_memberships:
            user = membership.user.email
            subject = 'Your PAPSAS Membership is Expiring Soon'
            message = f'Dear {membership.user.first_name},\n\nYour PAPSAS membership is set to expire in 3 days. Please renew your membership to continue enjoying our services.\n\nBest regards,\nPAPSAS Team'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [membership.user.email]
            
            send_mail(subject, message, from_email, recipient_list)
        
        self.stdout.write(self.style.SUCCESS(f'Sent notifications for {expiring_memberships.count()} expiring memberships'))