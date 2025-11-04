from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ..models_position import Position
from .serializers_position import PositionSerializer
from .permissions import IsAdminWrite


class PositionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly & IsAdminWrite]

    def get_queryset(self):
        qs = Position.objects.all()
        election_id = self.request.query_params.get("election") or self.kwargs.get("election_id")
        if election_id:
            qs = qs.filter(election_id=election_id)
        return qs

    def create(self, request, *args, **kwargs):
        election_id = self.kwargs.get("election_id") or request.data.get("electionId")
        if not election_id:
            return Response({"code": "MISSING_ELECTION", "message": "electionId required"}, status=status.HTTP_400_BAD_REQUEST)
        title = (request.data.get("title") or "").strip()
        if not title:
            return Response({"code": "VALIDATION_ERROR", "message": "title required"}, status=status.HTTP_400_BAD_REQUEST)
        enabled = bool(request.data.get("enabled", True))
        sort = int(request.data.get("sort", 0))
        pos = Position.objects.create(election_id=int(election_id), title=title, enabled=enabled, sort=sort)
        ser = PositionSerializer(pos)
        return Response(ser.data, status=status.HTTP_201_CREATED)

