from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from ...models import UserMembership
from ...views import get_expiring_memberships
import logging

class Command(BaseCommand):
    help = 'Check for memberships expiring in 3 days and send notifications'

    def handle(self, *args, **options):
        logging.basicConfig(filename='/Users/macbookairm1/Documents/capstone/papsas/papsas_app/management/log/command.log', level=logging.INFO,
                        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        
        expiring_memberships = get_expiring_memberships()
        logging.info(f'Found {expiring_memberships.count()} expiring memberships')
        self.stdout.write(self.style.SUCCESS(f'Sent notifications for {expiring_memberships.count()} expiring memberships'))
        
        for membership in expiring_memberships:
            user = membership.user.email
            subject = 'Your PAPSAS Membership is Expiring Soon'
            message = f'Dear {membership.user.first_name},\n\nYour PAPSAS membership is set to expire in 3 days. Please renew your membership to continue enjoying our services.\n\nBest regards,\nPAPSAS Team'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [membership.user.email]
            
            send_mail(subject, message, from_email, recipient_list)
        logging.info(f'Task completed. Sent {expiring_memberships.count()} notifications.')
        