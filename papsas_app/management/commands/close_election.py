from datetime import date
from django.core.management.base import BaseCommand
from papsas_app.models import Election
import logging

class Command(BaseCommand):
    help = 'Update election status for elections that have ended today'

    def handle(self, *args, **options):
        logging.basicConfig(filename='/var/www/papsas/papsas_app/management/log/command.log', level=logging.INFO,
                        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        today = date.today()
        elections = Election.objects.filter(endDate=today, electionStatus=True)
        logging.info(f'Found {elections.count()} closing election/s')
        self.stdout.write(f'Found {elections.count()} closing election/s')
        
        for election in elections:
            election.electionStatus = False
            election.save()
            self.stdout.write(f'Updated election {election.id} status to False')
        logging.info(f'Task completed. Closed {elections.count()} election/s.')
        