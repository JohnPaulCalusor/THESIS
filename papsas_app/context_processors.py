from datetime import date
from .models import User, Officer, Candidacy, Election, VisitorStats

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
        is_member = user.member.filter( expirationDate__gt=today, status = 'Approved' ).latest('id')
        days_until_expiration = (is_member.expirationDate - today).days
        # latest_pending_membership = user.member.filter(  status = 'Pending' ).latest('id')
    except:
        is_member = None
        days_until_expiration = None
    
    return {'is_member' : is_member,
        'days_until_expiration' : days_until_expiration,
        # 'latest_pending_membership' : latest_pending_membership
    }

def visitors_count(request):
    stats = VisitorStats.objects.first()
    return {'total_visitors': stats.total_visitors if stats else 0}