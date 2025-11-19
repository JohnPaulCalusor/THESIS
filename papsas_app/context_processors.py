from datetime import date
from .models import User, Officer, Candidacy, Election, VisitorStats

def is_officer(request):
    """
    Provides officer + admin info + openElection for navbar.
    """
    today = date.today()
    user = request.user

    officer = None
    openElection = Election.objects.none()
    is_admin_user = False

    if user.is_authenticated:
        # Admin = staff or in "admin" group
        try:
            groups = set(user.groups.values_list("name", flat=True))
        except Exception:
            groups = set()
        is_admin_user = user.is_staff or "admin" in groups

        openElection = Election.objects.filter(electionStatus=True)

        try:
            candidacy = Candidacy.objects.filter(candidate=user).latest("id")
            officer = Officer.objects.filter(candidateID=candidacy).latest("id")
        except (Officer.DoesNotExist, Candidacy.DoesNotExist):
            officer = None

    return {
        "officer": officer,
        "today": today,
        "openElection": openElection,
        "is_admin_user": is_admin_user,
    }


def is_member(request):
    user = request.user
    today = date.today()
    try:
        is_member = user.member.filter(
            expirationDate__gt=today,
            status="Approved",
        ).latest("id")
        days_until_expiration = (is_member.expirationDate - today).days
    except Exception:
        is_member = None
        days_until_expiration = None

    return {
        "is_member": is_member,
        "days_until_expiration": days_until_expiration,
    }


def visitors_count(request):
    stats = VisitorStats.objects.first()
    return {"total_visitors": stats.total_visitors if stats else 0}
