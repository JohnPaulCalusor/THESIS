from django.apps import apps
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class MyBallotView2(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, election_id):
        Election  = apps.get_model('papsas_app', 'Election')
        Candidacy = apps.get_model('papsas_app', 'Candidacy')
        Vote      = apps.get_model('papsas_app', 'Vote')

        e = get_object_or_404(Election, id=election_id)

        # If you've already voted in this election, return empty choices (mimic original behavior)
        if Vote.objects.filter(voterID=request.user, election=e).exists():
            return Response({"choices": []})

        # Active candidacies for this election
        qs = Candidacy.objects.filter(election=e, candidacyStatus=True).select_related()

        choices = []
        for c in qs:
            cand = c.candidate  # This is a User in your schema
            # Try to get a human name; fall back to username or string
            name = None
            candidate_id = None
            try:
                candidate_id = getattr(cand, "id", None)
                name = (getattr(cand, "get_full_name", lambda: None)() or
                        getattr(cand, "fullName", None) or
                        getattr(cand, "username", None))
            except Exception:
                pass
            if not name:
                name = str(cand)
            choices.append({
                "candidacyId": c.id,
                "candidateId": candidate_id,
                "name": name,
                "credentials": c.credentials,
            })

        return Response({"choices": choices})
