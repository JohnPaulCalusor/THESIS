from .views_results import ElectionResultsView
from django.urls import path

# Core/auth/me views
from .views import (
    health, LoginView, RefreshView, MeView,
    ElectionListView, BallotView, VoteView, ResultsView,
)

# Current election + candidacy quick-create
from .views_candidacy import CurrentElectionView, CandidacyQuickCreate

# Positions list/detail
from .views_position import PositionViewSet

# User search (admin-only)
from .views_user import UserSearchView

# Map viewset actions for positions
position_list = PositionViewSet.as_view({"get": "list", "post": "create"})
position_detail = PositionViewSet.as_view({"patch": "partial_update", "delete": "destroy"})

urlpatterns = [
    # Health
    path("health", health, name="api-health"),

    # Auth
    path("auth/login/",   LoginView.as_view(),   name="api-login"),
    path("auth/refresh/", RefreshView.as_view(), name="api-refresh"),

    # Me
    path("me/", MeView.as_view(), name="api-me"),

    # Canonical election endpoints
    path("elections/", ElectionListView.as_view(), name="elections-list"),
    path("elections/current", CurrentElectionView.as_view(), name="elections-current"),
    path("elections/<int:election_id>/ballot", BallotView.as_view(), name="election-ballot"),
    path("elections/<int:election_id>/vote", VoteView.as_view(), name="election-vote"),
    path("elections/<int:election_id>/results", ElectionResultsView.as_view(), name="election-results"),

    # Positions
    path("elections/<int:election_id>/positions", position_list, name="positions-list-create"),
    path("positions/<int:pk>", position_detail, name="positions-detail"),

    # Candidacy quick-create
    path("elections/<int:id>/candidacies/quick", CandidacyQuickCreate.as_view(), name="candidacies-quick"),

    # Users search (admin-only)
    path("users", UserSearchView.as_view(), name="user-search"),
]
