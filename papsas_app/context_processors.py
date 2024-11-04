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

def is_member(request):
    user = request.user
    today = date.today()
    try:
        is_member = user.member.filter( expirationDate__gt=today).latest('id')
        if is_member:
            print(True)
    except:
        is_member = None
    
    return {'is_member' : is_member}
