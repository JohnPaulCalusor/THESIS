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

from rest_framework import status

class CastVoteView2(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, election_id):
        Election  = apps.get_model('papsas_app', 'Election')
        Candidacy = apps.get_model('papsas_app', 'Candidacy')
        Vote      = apps.get_model('papsas_app', 'Vote')
        User      = apps.get_model('papsas_app', 'User')

        e = get_object_or_404(Election, id=election_id)

        # Already voted?
        if Vote.objects.filter(voterID=request.user, election=e).exists():
            return Response({"detail": "You already voted in this election."},
                            status=status.HTTP_400_BAD_REQUEST)

        candidacy_id = request.data.get('candidacyId')
        if not candidacy_id:
            return Response({"detail": "candidacyId is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        c = get_object_or_404(Candidacy, id=candidacy_id, election=e, candidacyStatus=True)
        candidate_user = c.candidate  # in your schema, this is a User

        # Find the FK on Vote that points to User and represents the chosen candidate
        candidate_fk = None
        for f in Vote._meta.get_fields():
            if getattr(f, 'is_relation', False) and getattr(f, 'many_to_one', False) and f.related_model == User:
                if f.name in ('candidateID','candidate','candidate_user','candidateId'):
                    candidate_fk = f.name
                    break
        if not candidate_fk:
            # fallback to any User FK other than voterID
            for f in Vote._meta.get_fields():
                if getattr(f, 'is_relation', False) and getattr(f, 'many_to_one', False) and f.related_model == User and f.name != 'voterID':
                    candidate_fk = f.name
                    break
        if not candidate_fk:
            VoteSelection = apps.get_model("papsas_app", "VoteSelection")
            vote = Vote.objects.create(voterID=request.user, election=e)
            VoteSelection.objects.create(vote=vote, candidate=candidate_user)
            return Response({"ok": True, "voteId": vote.id}, status=status.HTTP_201_CREATED)

        vote = Vote.objects.create(voterID=request.user, election=e, **{candidate_fk: candidate_user})
        return Response({"ok": True, "voteId": vote.id}, status=status.HTTP_201_CREATED)


class ElectionResults2(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, election_id):
        Election  = apps.get_model('papsas_app', 'Election')
        Candidacy = apps.get_model('papsas_app', 'Candidacy')
        Vote      = apps.get_model('papsas_app', 'Vote')
        User      = apps.get_model('papsas_app', 'User')

        e = get_object_or_404(Election, id=election_id)

        # detect candidate FK on Vote
        candidate_fk = None
        for f in Vote._meta.get_fields():
            if getattr(f, 'is_relation', False) and getattr(f, 'many_to_one', False) and f.related_model == User and f.name != 'voterID':
                candidate_fk = f.name
                if f.name in ('candidateID','candidate','candidate_user','candidateId'):
                    break

        results = []
        for c in Candidacy.objects.filter(election=e, candidacyStatus=True).select_related():
            name = (getattr(c.candidate, "get_full_name", lambda: None)() or
                    getattr(c.candidate, "username", None) or str(c.candidate))
            if candidate_fk:
                # count directly on Vote when a candidate FK exists
                vote_count = Vote.objects.filter(election=e, **{candidate_fk: c.candidate}).count()
            else:
                # fallback: count via VoteSelection (vote -> selection -> candidate)
                VoteSelection = apps.get_model('papsas_app', 'VoteSelection')
                vote_count = VoteSelection.objects.filter(
                    vote__election=e,
                    candidate=c.candidate,
                ).count()

            results.append({"candidacyId": c.id, "name": name, "votes": vote_count})

        results.sort(key=lambda r: r["votes"], reverse=True)
        return Response({"election": {"id": e.id, "title": e.title}, "results": results})
