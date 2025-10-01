from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from papsas_app.models import Election, Candidacy
from .serializers import ElectionSerializer, CandidacySerializer

class ElectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Election.objects.all().order_by("id")
    serializer_class = ElectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # change to AllowAny if you want public read

    @action(detail=True, methods=["get"], authentication_classes=[JWTAuthentication], permission_classes=[permissions.IsAuthenticated])
    def candidates(self, request, pk=None):
        qs = Candidacy.objects.filter(election_id=pk).order_by("id")
        return Response(CandidacySerializer(qs, many=True).data)
