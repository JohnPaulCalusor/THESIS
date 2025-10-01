from rest_framework.serializers import ModelSerializer
from papsas_app.models import Election, Candidacy

class ElectionSerializer(ModelSerializer):
    class Meta:
        model = Election
        fields = "__all__"

class CandidacySerializer(ModelSerializer):
    class Meta:
        model = Candidacy
        fields = "__all__"
