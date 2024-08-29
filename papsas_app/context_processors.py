from datetime import date
from .models import User, Officer, Candidacy, Election

def is_officer(request):
    today = date.today()
    user = request.user
    openElection = Election.objects.none() 
    if user.is_authenticated:
        openElection = Election.objects.filter( electionStatus = True)
        try:
            candidacy = Candidacy.objects.filter( candidate = user).latest('id')
            officer = Officer.objects.filter( candidateID = candidacy ).latest('id')
        except (Officer.DoesNotExist, Candidacy.DoesNotExist):
            officer = None
    else:
        officer = None

    return {'officer' : officer, 'today' : today, 'openElection': openElection}