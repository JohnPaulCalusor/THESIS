from rest_framework import serializers
from ..models_position import Position


class PositionSerializer(serializers.ModelSerializer):
    electionId = serializers.IntegerField(source="election_id", read_only=True)

    class Meta:
        model = Position
        fields = ("id", "electionId", "title", "enabled", "sort")

