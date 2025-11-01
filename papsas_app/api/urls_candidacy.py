from django.urls import path
from .views_candidacy import (
    CurrentElectionView, ElectionCandidacyListCreate, CandidacyDetail, CandidacyQuickCreate
)
urlpatterns = [
    path('elections/current', CurrentElectionView.as_view()),
    path('elections/<int:id>/candidacies', ElectionCandidacyListCreate.as_view()),
    path('elections/<int:id>/candidacies/quick', CandidacyQuickCreate.as_view()),
    path('candidacies/<int:cid>', CandidacyDetail.as_view()),
]
