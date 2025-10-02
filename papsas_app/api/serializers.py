from rest_framework import serializers
from ..models import Election, Candidate

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        # Use the fields you’ve been returning in your working responses
        fields = ["id", "title", "startDate", "endDate", "electionStatus", "numWinners"]

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        # Safe choice; refine later if you want to limit fields
        fields = "__all__"
