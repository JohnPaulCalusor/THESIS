from django.urls import path
from .views import (
    health, LoginView, RefreshView, MeView,
    ElectionListView, ElectionDetailView,
    MyBallotView, VoteView, ResultsView
)

urlpatterns = [
    path("health", health, name="api-health"),

    # Auth
    path("auth/login/",   LoginView.as_view(),   name="api-login"),
    path("auth/refresh/", RefreshView.as_view(), name="api-refresh"),

    # Me
    path("me/", MeView.as_view(), name="api-me"),

    # Elections
    path("elections/",                   ElectionListView.as_view(),   name="api-elections"),
    path("elections/<int:pk>/",          ElectionDetailView.as_view(), name="api-election-detail"),
    path("elections/<int:election_id>/ballot", MyBallotView.as_view(), name="api-election-ballot"),
    path("elections/<int:election_id>/vote/",  VoteView.as_view(),     name="api-election-vote"),
    path("elections/<int:election_id>/results", ResultsView.as_view(), name="api-election-results"),
]
