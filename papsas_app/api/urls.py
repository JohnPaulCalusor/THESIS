from papsas_app.views_vote_json import api_vote_json
# from .views_candidacy_admin import CandidacyListView
from .views_ballot import ElectionBallotView
from django.urls import path

# Core/auth/me views
from .views import (
    LoginView,
    RefreshView,
    MeView,
    EmailVerificationStartView,
    EmailVerificationVerifyView,
    ElectionListView,
    VoteView,
    ResultsView,
)
from .views_health import HealthView



# Current election + candidacy quick-create
from .views_candidacy import CurrentElectionView, CandidacyQuickCreate
from .views_results import ElectionResultsView, ElectionResultsCsvView
from .views_analytics import election_analytics, ElectionExplainView
from papsas_app.analytics.views import audit_events, audit_export_csv
from .views_events import event_detail, events_ics, events_list
from .views_event_registration import EventRegistrationView
from .views_candidacy_admin import CandidacyListCreateView, CandidacyDetailPatchView
from .views_candidacy import candidacy_partial_update

# Positions list/detail
from .views_position import PositionViewSet

# User search (admin-only)
from .views_user import UserSearchView

# Map viewset actions for positions
position_list = PositionViewSet.as_view({"get": "list", "post": "create"})
position_detail = PositionViewSet.as_view({"patch": "partial_update", "delete": "destroy"})

urlpatterns = [
    path('elections/<int:eid>/vote', api_vote_json),
# (shadowed)     path("elections/<int:election_id>/candidacies", CandidacyListView.as_view(), name="election-candidacies"),
    # Health
    path("health", HealthView.as_view(), name="api-health"),

    path("events", events_list, name="api-events-list"),
    path("events/<slug:slug>", event_detail, name="api-events-detail"),
    path("events.ics", events_ics, name="api-events-ics"),
    path("events/<int:event_id>/registration", EventRegistrationView.as_view(), name="event-registration"),
    path("events/<int:event_id>/registration/", EventRegistrationView.as_view()),

    # Auth
    path("auth/email/start", EmailVerificationStartView.as_view(), name="api-auth-email-start"),
    path("auth/email/start/", EmailVerificationStartView.as_view()),
    path("auth/email/verify", EmailVerificationVerifyView.as_view(), name="api-auth-email-verify"),
    path("auth/email/verify/", EmailVerificationVerifyView.as_view()),
    path("auth/me", MeView.as_view(), name="api-auth-me"),
    path("auth/me/", MeView.as_view()),
    path("auth/login/",   LoginView.as_view(),   name="api-login"),
    path("auth/refresh/", RefreshView.as_view(), name="api-refresh"),

    # Me
    path("me", MeView.as_view(), name="api-me"),
    path("me/", MeView.as_view()),

    # Canonical election endpoints
    path("elections/", ElectionListView.as_view(), name="elections-list"),
    path("elections/current", CurrentElectionView.as_view(), name="elections-current"),
    path("elections/<int:election_id>/ballot", ElectionBallotView.as_view(), name="election-ballot"),
    path("elections/<int:election_id>/vote", VoteView.as_view(), name="election-vote"),
    path("elections/<int:election_id>/results", ElectionResultsView.as_view(), name="election-results"),
    path("elections/<int:election_id>/results/export.csv", ElectionResultsCsvView.as_view(), name="election-results-csv"),
    path("elections/<int:election_id>/analytics", election_analytics, name="election-analytics"),
    path("elections/<int:election_id>/explain",   ElectionExplainView.as_view(),   name="election-explain"),
    path("audit/events", audit_events),
    path("audit/events/export.csv", audit_export_csv),

    # Positions
    path("elections/<int:election_id>/positions", position_list, name="positions-list-create"),
    path("positions/<int:pk>", position_detail, name="positions-detail"),

    # Candidacy quick-create
    path("elections/<int:id>/candidacies/quick", CandidacyQuickCreate.as_view(), name="candidacies-quick"),

    # Candidacies admin write path + list
    path("elections/<int:election_id>/candidacies", CandidacyListCreateView.as_view()),
    path("elections/<int:election_id>/candidacies/<int:pk>", CandidacyDetailPatchView.as_view()),
    # compat: slashless PATCH + DELETE used by legacy tests
    path("candidacies/<int:pk>", candidacy_partial_update, name="candidacy-partial-update-noslash"),

    # Users search (admin-only)
    path("users", UserSearchView.as_view(), name="user-search"),
]
