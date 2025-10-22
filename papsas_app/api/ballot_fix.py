from django.apps import apps
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

def _get_election_id(kwargs):
    # accept either /elections/<int:election_id>/... or /elections/<int:id>/...
    return kwargs.get("election_id") or kwargs.get("id")

class MyBallotView2(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        election_id = _get_election_id(kwargs)
        Election  = apps.get_model('papsas_app', 'Election')
        Candidacy = apps.get_model('papsas_app', 'Candidacy')
        Vote      = apps.get_model('papsas_app', 'Vote')

        e = get_object_or_404(Election, id=election_id)

        # If you've already voted in this election, return empty choices
        if Vote.objects.filter(voterID=request.user, election=e).exists():
            return Response({"choices": []})

        qs = Candidacy.objects.filter(election=e, candidacyStatus=True).select_related()

        choices = []
        for c in qs:
            cand = c.candidate  # User
            # best-effort display name
            name = None
            candidate_id = getattr(cand, "id", None)
            try:
                name = (
                    getattr(cand, "get_full_name", lambda: None)()
                    or getattr(cand, "fullName", None)
                    or getattr(cand, "username", None)
                )
            except Exception:
                pass
            if not name:
                name = str(cand)
            choices.append({
                "candidacyId": c.id,
                "candidateId": candidate_id,
                "name": name,
                "credentials": getattr(c, "credentials", None),
            })

        return Response({"choices": choices})

class CastVoteView2(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        election_id = _get_election_id(kwargs)
        Election  = apps.get_model('papsas_app', 'Election')
        Candidacy = apps.get_model('papsas_app', 'Candidacy')
        Vote      = apps.get_model('papsas_app', 'Vote')
        User      = apps.get_model('papsas_app', 'User')

        e = get_object_or_404(Election, id=election_id)

        if Vote.objects.filter(voterID=request.user, election=e).exists():
            return Response({"detail": "You already voted in this election."},
                            status=status.HTTP_400_BAD_REQUEST)

        candidacy_id = request.data.get('candidacyId')
        if not candidacy_id:
            return Response({"detail": "candidacyId is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        c = get_object_or_404(Candidacy, id=candidacy_id, election=e, candidacyStatus=True)
        candidate_user = c.candidate  # User

        # Prefer a direct FK on Vote to User (chosen candidate); otherwise fall back to M2M.
        candidate_fk = None
        for f in Vote._meta.get_fields():
            if getattr(f, 'is_relation', False) and getattr(f, 'many_to_one', False) and f.related_model == User:
                if f.name in ('candidateID', 'candidate', 'candidate_user', 'candidateId'):
                    candidate_fk = f.name
                    break
        if not candidate_fk:
            for f in Vote._meta.get_fields():
                if getattr(f, 'is_relation', False) and getattr(f, 'many_to_one', False) and f.related_model == User and f.name != 'voterID':
                    candidate_fk = f.name
                    break

        if candidate_fk:
            vote = Vote.objects.create(voterID=request.user, election=e, **{candidate_fk: candidate_user})
            return Response({"ok": True, "voteId": vote.id}, status=status.HTTP_201_CREATED)

        # Else: support M2M on Vote → User or Vote → Candidacy
        m2m_field = None
        m2m_target = None
        for f in Vote._meta.get_fields():
            if getattr(f, 'many_to_many', False) and getattr(f, 'is_relation', False):
                if f.related_model in (User, Candidacy):
                    m2m_field = f.name
                    m2m_target = f.related_model
                    # prefer likely names
                    if f.name in ('candidateID', 'candidates', 'selected', 'selections'):
                        break

        if m2m_field:
            vote = Vote.objects.create(voterID=request.user, election=e)
            if m2m_target.__name__ == 'User':
                getattr(vote, m2m_field).add(candidate_user)
            else:  # Candidacy
                getattr(vote, m2m_field).add(c)
            return Response({"ok": True, "voteId": vote.id}, status=status.HTTP_201_CREATED)

        return Response({"detail": "Vote schema does not have a candidate FK or M2M that the API recognizes."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ElectionResults2(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        election_id = _get_election_id(kwargs)
        Election  = apps.get_model('papsas_app', 'Election')
        Candidacy = apps.get_model('papsas_app', 'Candidacy')
        Vote      = apps.get_model('papsas_app', 'Vote')
        User      = apps.get_model('papsas_app', 'User')

        e = get_object_or_404(Election, id=election_id)

        # Detect direct FK (Vote → User) for chosen candidate
        candidate_fk = None
        for f in Vote._meta.get_fields():
            if getattr(f, 'is_relation', False) and getattr(f, 'many_to_one', False) and f.related_model == User and f.name != 'voterID':
                candidate_fk = f.name
                if f.name in ('candidateID', 'candidate', 'candidate_user', 'candidateId'):
                    break

        # Detect M2M (Vote → User or Vote → Candidacy)
        m2m_field = None
        m2m_target = None
        for f in Vote._meta.get_fields():
            if getattr(f, 'many_to_many', False) and getattr(f, 'is_relation', False):
                if f.related_model in (User, Candidacy):
                    m2m_field = f.name
                    m2m_target = f.related_model
                    if f.name in ('candidateID', 'candidates', 'selected', 'selections'):
                        break

        results = []
        for c in Candidacy.objects.filter(election=e, candidacyStatus=True).select_related():
            name = (
                getattr(c.candidate, "get_full_name", lambda: None)()
                or getattr(c.candidate, "username", None)
                or str(c.candidate)
            )

            if candidate_fk:
                vote_count = Vote.objects.filter(election=e, **{candidate_fk: c.candidate}).count()
            elif m2m_field:
                if m2m_target.__name__ == 'User':
                    vote_count = Vote.objects.filter(election=e, **{f"{m2m_field}": c.candidate}).count()
                else:
                    vote_count = Vote.objects.filter(election=e, **{f"{m2m_field}": c}).count()
            else:
                vote_count = 0

            results.append({"candidacyId": c.id, "name": name, "votes": vote_count})

        results.sort(key=lambda r: r["votes"], reverse=True)
        return Response({"election": {"id": e.id, "title": e.title}, "results": results})
