from rest_framework import viewsets, permissions, decorators, response
from ..models import Election, Candidate
from .serializers import ElectionSerializer, CandidateSerializer

class ElectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Election.objects.all().order_by("id")
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=True, methods=["get"])
    def candidates(self, request, pk=None):
        qs = Candidate.objects.filter(election_id=pk).order_by("id")
        return response.Response(CandidateSerializer(qs, many=True).data)
