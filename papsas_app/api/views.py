from rest_framework import permissions, viewsets
from papsas_app.models import Election
from .serializers import ElectionSerializer

class ElectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Election.objects.all().order_by("id")
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAuthenticated]
