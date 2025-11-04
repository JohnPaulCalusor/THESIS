from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from django.apps import apps

from papsas_app.models import Election, Candidacy
from .serializers_candidacy import CandidacyReadSerializer, CandidacyWriteSerializer, _pos_field, _user_field
from .permissions import IsAdminOnly, IsAdminWrite, IsOfficerOrAdmin, IsOfficerOrAdminRead
from .api_errors import error_response

User = get_user_model()

def _fk_name_to(model, to_model):
    """Return the FK field name in `model` that points to `to_model`, else None."""
    for f in model._meta.get_fields():
        if getattr(f, "many_to_one", False):
            m = getattr(getattr(f, "remote_field", None), "model", None)
            if m is to_model:
                return f.name
    return None

class CurrentElectionView(APIView):
    def get(self, request):
        today = timezone.now().date()
        qs = Election.objects.filter(
            electionStatus=True, startDate__lte=today, endDate__gte=today
        ).order_by('endDate','id')
        if not qs.exists():
            return error_response('NOT_FOUND', 'No open election.')
        e = qs.first()
        return Response({
            'id': e.id,
            'title': getattr(e, 'title', None),
            'startDate': getattr(e, 'startDate', None),
            'endDate': getattr(e, 'endDate', None),
            'electionStatus': getattr(e, 'electionStatus', None),
            'numWinners': getattr(e, 'numWinners', None),
        })

class ElectionCandidacyListCreate(APIView):
    permission_classes = [IsOfficerOrAdminRead, IsAdminWrite]

    def get_permissions(self):
        # Officers/Admin can READ; only Admin can WRITE
        if self.request.method in ("GET","HEAD","OPTIONS"):
            return [IsOfficerOrAdmin()]
        return [IsAdminOnly()]
    def get(self, request, id):
        election = get_object_or_404(Election, id=id)
        qs = Candidacy.objects.filter(election=election).order_by('id')
        return Response({
            'election': {'id': election.id, 'title': getattr(election, 'title', None)},
            'results': CandidacyReadSerializer(qs, many=True).data
        })

    def post(self, request, id):
        try:
            election = get_object_or_404(Election, id=id)
            ser = CandidacyWriteSerializer(data=request.data, context={'election': election, 'is_create': True})
            if not ser.is_valid():
                errs = ser.errors
                if 'non_field_errors' in errs and 'ALREADY_EXISTS' in errs['non_field_errors']:
                    return error_response('ALREADY_EXISTS', 'Candidacy already exists for this context.')
                return error_response('VALIDATION_ERROR', str(errs))
            try:
                obj = ser.save()
            except IntegrityError:
                return error_response('ALREADY_EXISTS', 'Candidacy already exists for this context.')
            return Response(CandidacyReadSerializer(obj).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return error_response('VALIDATION_ERROR', f'{e}')

class CandidacyDetail(APIView):
    permission_classes = [IsOfficerOrAdminRead, IsAdminWrite]

    def patch(self, request, cid):
        try:
            obj = get_object_or_404(Candidacy, id=cid)
            ser = CandidacyWriteSerializer(obj, data=request.data, partial=True)
            if not ser.is_valid():
                errs = ser.errors
                if 'non_field_errors' in errs and 'ALREADY_EXISTS' in errs['non_field_errors']:
                    return error_response('ALREADY_EXISTS', 'Candidacy already exists for this context.')
                return error_response('VALIDATION_ERROR', str(errs))
            obj = ser.save()
            return Response(CandidacyReadSerializer(obj).data)
        except Exception as e:
            return error_response('VALIDATION_ERROR', f'{e}')

    def delete(self, request, cid):
        try:
            obj = get_object_or_404(Candidacy, id=cid)

            # Protect delete if votes reference this candidacy
            has_votes = False

            VS = apps.get_model('papsas_app', 'VoteSelection')
            if VS:
                fk = _fk_name_to(VS, Candidacy)
                if fk:
                    filt = {f"{fk}_id": obj.id}
                    has_votes = VS.objects.filter(**filt).exists()

            if not has_votes:
                V = apps.get_model('papsas_app', 'Vote')
                if V:
                    fk = _fk_name_to(V, Candidacy)
                    if fk:
                        filt = {f"{fk}_id": obj.id}
                        has_votes = V.objects.filter(**filt).exists()

            if has_votes:
                return error_response('HAS_VOTES', 'Cannot delete candidacy with recorded votes.')

            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return error_response('VALIDATION_ERROR', f'{e}')

class CandidacyQuickCreate(APIView):
    permission_classes = [IsOfficerOrAdminRead, IsAdminWrite]

    def post(self, request, id):
        try:
            election = get_object_or_404(Election, id=id)
            payload = request.data or {}
            position_id = payload.get('positionId')
            name = (payload.get('name') or '').strip()
            email = (payload.get('email') or '').strip().lower()
            credentials = payload.get('credentials', '')
            status_flag = payload.get('status', True)

            if _pos_field() and not position_id:
                return error_response('VALIDATION_ERROR', 'positionId is required.')
            if not name or not email:
                return error_response('VALIDATION_ERROR', 'Both name and email are required.')
            if User.objects.filter(email__iexact=email).exists():
                return error_response('EMAIL_TAKEN', 'Email already in use.')

            first, last = name, ''
            if ',' in name:
                last, first = [p.strip() for p in name.split(',', 1)]
            elif ' ' in name:
                first, last = name.rsplit(' ', 1)

            user = User.objects.create(username=email, email=email, first_name=first, last_name=last, is_active=False)
            user.set_unusable_password()
            user.save()

            if getattr(election, 'organization_id', None):
                prof = getattr(user, 'profile', None)
                if prof and hasattr(prof, 'organization_id'):
                    prof.organization_id = election.organization_id
                    prof.save(update_fields=['organization_id'])

            pf = _pos_field()
            kwargs = {'election': election, 'credentials': credentials, 'status': bool(status_flag)}
            if pf:
                pos_model = pf.remote_field.model
                position = pos_model.objects.get(id=position_id)
                kwargs.update({pf.name: position})
            uf = _user_field()
            kwargs.update({uf.name: user})

            try:
                from django.db import transaction
                with transaction.atomic():
                    # Simple app-level duplicate check
                    exists = Candidacy.objects.filter(
                        election=election,
                        **({pf.name: kwargs[pf.name]} if pf else {}),
                        **{uf.name: user}
                    ).exists()
                    if exists:
                        return error_response('ALREADY_EXISTS', 'Candidacy already exists for this context.')
                    cand = Candidacy.objects.create(**kwargs)
            except IntegrityError:
                return error_response('ALREADY_EXISTS', 'Candidacy already exists for this context.')

            return Response({'user_id': user.id, 'candidacy_id': cand.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return error_response('VALIDATION_ERROR', f'{e}')
