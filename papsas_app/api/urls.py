from .ballot_fix import MyBallotView2, CastVoteView2, ElectionResults2
from .ballot_fix import MyBallotView2
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
    path("elections/<int:election_id>/ballot", MyBallotView2.as_view(), name="api-election-ballot"),
    path("elections/<int:election_id>/vote/",  VoteView.as_view(),     name="api-election-vote"),
    path("elections/<int:election_id>/results", ElectionResults2.as_view(), name="api-election-results"),
]


urlpatterns += [
    path('elections/<int:election_id>/ballot2', MyBallotView2.as_view(), name='ballot2'),
]

urlpatterns += [
    path('elections/<int:election_id>/vote', CastVoteView2.as_view(), name='api-election-vote2'),
    path('elections/<int:election_id>/results2', ElectionResults2.as_view(), name='api-election-results2'),
]

urlpatterns += [
    path('elections/<int:election_id>/results', ElectionResults2.as_view(), name='api-election-results'),
]
