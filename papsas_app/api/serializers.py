from rest_framework import serializers
from papsas_app.models import Election

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ("id", "title", "startDate", "endDate", "electionStatus", "numWinners")
