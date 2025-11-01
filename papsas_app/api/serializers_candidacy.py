from django.contrib.auth import get_user_model
from rest_framework import serializers
from papsas_app.models import Candidacy, Election

User = get_user_model()

def _pos_field():
    # Prefer FK whose name or model name contains position/role/office/post
    for f in Candidacy._meta.get_fields():
        if getattr(f, "many_to_one", False):
            m = getattr(getattr(f, "remote_field", None), "model", None)
            if not m:
                continue
            label = (f.name + " " + m.__name__).lower()
            if any(k in label for k in ("position", "role", "office", "post")):
                return f
    # Fallback: first FK that's not election and not to User
    for f in Candidacy._meta.get_fields():
        if getattr(f, "many_to_one", False):
            m = getattr(getattr(f, "remote_field", None), "model", None)
            if f.name != "election" and m and m is not User:
                return f
    return None  # no position FK

def _user_field():
    # FK to AUTH_USER_MODEL
    for f in Candidacy._meta.get_fields():
        if getattr(f, "many_to_one", False):
            m = getattr(getattr(f, "remote_field", None), "model", None)
            if m is User:
                return f
    return None

def _has_db_field(name: str) -> bool:
    return any(f.name == name for f in Candidacy._meta.fields)

class CandidacyReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    position_id = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    candidate_user_id = serializers.SerializerMethodField()
    candidate_name = serializers.SerializerMethodField()
    credentials = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_position_id(self, obj):
        pf = _pos_field()
        if not pf:
            return None
        pos = getattr(obj, pf.name, None)
        return getattr(pos, "id", None)

    def get_position_title(self, obj):
        pf = _pos_field()
        if not pf:
            return None
        pos = getattr(obj, pf.name, None)
        if not pos:
            return None
        return getattr(pos, "title", None) or getattr(pos, "name", None) or str(pos)

    def get_candidate_user_id(self, obj):
        uf = _user_field()
        u = getattr(obj, uf.name) if uf else None
        return getattr(u, "id", None)

    def get_candidate_name(self, obj):
        uf = _user_field()
        u = getattr(obj, uf.name) if uf else None
        if not u:
            return None
        last = getattr(u, 'last_name', '') or ''
        first = getattr(u, 'first_name', '') or ''
        if last or first:
            return f"{last}, {first}".strip(", ")
        return getattr(u, 'email', None) or getattr(u, 'username', None)

    def get_credentials(self, obj):
        return getattr(obj, 'credentials', None)

    def get_status(self, obj):
        return getattr(obj, 'status', None)

class CandidacyWriteSerializer(serializers.Serializer):
    positionId = serializers.IntegerField(required=False)
    candidateUserId = serializers.IntegerField(required=False)
    credentials = serializers.CharField(required=False, allow_blank=True, max_length=500)
    status = serializers.BooleanField(required=False)

    def validate(self, data):
        is_create = self.context.get('is_create')
        pf_exists = _pos_field() is not None
        if is_create:
            if pf_exists and 'positionId' not in data:
                raise serializers.ValidationError({'positionId': 'This field is required.'})
            if 'candidateUserId' not in data:
                raise serializers.ValidationError({'candidateUserId': 'This field is required.'})
        return data

    def create(self, validated):
        election: Election = self.context['election']
        pf = _pos_field()
        uf = _user_field()
        if not uf:
            raise serializers.ValidationError({'non_field_errors':'Candidacy model missing candidate/user relation.'})

        user = User.objects.get(id=validated['candidateUserId'])

        # Optional org guard
        if getattr(election, 'organization_id', None):
            prof = getattr(user, 'profile', None)
            user_org_id = getattr(prof, 'organization_id', None)
            if user_org_id != election.organization_id:
                raise serializers.ValidationError({'candidateUserId': 'Candidate not in election organization.'})

        # Build kwargs ONLY with real DB fields
        kwargs = {'election': election}
        if pf:
            pos_model = pf.remote_field.model
            position = pos_model.objects.get(id=validated['positionId'])
            kwargs[pf.name] = position

        if _has_db_field('credentials') and 'credentials' in validated:
            kwargs['credentials'] = validated['credentials']
        if _has_db_field('status') and 'status' in validated:
            kwargs['status'] = validated['status']

        # Uniqueness check
        check = {'election': election, uf.name: user}
        if pf:
            check[pf.name] = kwargs[pf.name]
        if Candidacy.objects.filter(**check).exists():
            raise serializers.ValidationError({'non_field_errors':'ALREADY_EXISTS'})

        kwargs[uf.name] = user
        obj = Candidacy.objects.create(**kwargs)
        return obj

    def update(self, instance: Candidacy, validated):
        pf = _pos_field()
        uf = _user_field()

        if pf and 'positionId' in validated:
            pos_model = pf.remote_field.model
            new_pos = pos_model.objects.get(id=validated['positionId'])
            # pre-check duplicate
            check = {pf.name: new_pos, uf.name: getattr(instance, uf.name)}
            if Candidacy.objects.exclude(id=instance.id).filter(election=instance.election, **check).exists():
                raise serializers.ValidationError({'non_field_errors': 'ALREADY_EXISTS'})
            setattr(instance, pf.name, new_pos)

        if _has_db_field('credentials') and 'credentials' in validated:
            instance.credentials = validated['credentials']
        if _has_db_field('status') and 'status' in validated:
            instance.status = validated['status']

        instance.save()
        return instance
