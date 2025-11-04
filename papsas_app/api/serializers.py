from django.utils import timezone
from django.apps import apps
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import CharField, TextField

User = get_user_model()

# ---------- helpers ----------
def find_model(app_label, prefer_names, contains_hint):
    for name in prefer_names:
        try:
            return apps.get_model(app_label, name)
        except LookupError:
            pass
    for m in apps.get_app_config(app_label).get_models():
        if contains_hint.lower() in m.__name__.lower():
            return m
    available = [m.__name__ for m in apps.get_app_config(app_label).get_models()]
    raise ImportError(f"Couldn't find model like {prefer_names} ({contains_hint}) in {app_label}. Have: {available}")

def fk_field(model, to_model):
    for f in model._meta.get_fields():
        if getattr(f, "many_to_one", False) and getattr(getattr(f, "remote_field", None), "model", None) == to_model:
            return f
    return None

def pick_attr(obj, names):
    for n in names:
        if hasattr(obj, n):
            v = getattr(obj, n)
            return v() if callable(v) else v
    return None

# ---------- resolve your models ----------
APP = "papsas_app"
Election   = find_model(APP, ("Election",), "elect")
Candidate  = find_model(APP, ("Candidacy","Candidate","Nominee","Aspirant"), "cand")
VoteModel  = find_model(APP, ("Vote","Votes"), "vote")

# Candidacy -> Election FK name (required)
cand_fk_to_election = fk_field(Candidate, Election)
if not cand_fk_to_election:
    raise ImportError("Your Candidacy/Candidate model must have a ForeignKey to Election.")
cand_elec_fk_name = cand_fk_to_election.name

# Find the text field on Candidacy that stores the position/office/role label
def _find_position_label_field(model):
    preferred = ("position","office","role","title","seat","post","position_name")
    # try preferred names first
    for f in model._meta.get_fields():
        if isinstance(getattr(f, "target_field", f), (CharField, TextField)):
            if f.name in preferred:
                return f.name
    # fallback: any CharField/TextField with choices or reasonable length
    for f in model._meta.get_fields():
        tf = getattr(f, "target_field", f)
        if isinstance(tf, (CharField, TextField)):
            return f.name
    raise ImportError("Could not find a text field on Candidacy that looks like a position/office label.")
position_label_field = _find_position_label_field(Candidate)

# ---------- user mini serializer ----------
def _role_of(user):
    role = getattr(user, "role", None)
    if role: return role
    if getattr(user, "is_superuser", False): return "admin"
    if getattr(user, "is_staff", False):     return "officer"
    return "member"

class UserLiteSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    is_officer = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "email", "role", "is_member", "is_officer"]
    def get_role(self, obj): return _role_of(obj)
    def get_is_member(self, obj): return bool(getattr(obj, "is_member", False))
    def get_is_officer(self, obj): return bool(getattr(obj, "is_officer", False) or getattr(obj, "is_staff", False))

# ---------- display helpers ----------
def candidate_name(obj):
    name = pick_attr(obj, ["name","full_name","candidate_name","title","label"])
    if name: return name
    try:
        user_fk = next(
            f.name for f in obj._meta.get_fields()
            if getattr(f, "many_to_one", False) and getattr(getattr(f, "remote_field", None), "model", None) == User
        )
        u = getattr(obj, user_fk, None)
        if u:
            return (getattr(u, "get_full_name", lambda: None)() or
                    getattr(u, "username", None) or
                    getattr(u, "email", None) or str(u))
    except StopIteration:
        pass
    return str(obj)

# ---------- API serializers ----------
class CandidateSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    class Meta:
        model = Candidate
        fields = ["id", "name", "position"]
    def get_name(self, obj): return candidate_name(obj)
    def get_position(self, obj): return getattr(obj, position_label_field, None)

# Synthetic "position block" (since positions are labels, not a model)
class PositionBlockSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    candidates = CandidateSerializer(many=True)

class ElectionListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    class Meta:
        model = Election
        fields = ["id", "title", "opens_at", "closes_at", "status"]
    def get_status(self, obj):
        now = timezone.now()
        if obj.opens_at and now < obj.opens_at: return "upcoming"
        if obj.closes_at and now > obj.closes_at: return "closed"
        return "open"

class ElectionDetailSerializer(ElectionListSerializer):
    positions = serializers.SerializerMethodField()
    class Meta(ElectionListSerializer.Meta):
        fields = ["id", "title", "opens_at", "closes_at", "status", "positions"]

    def get_positions(self, obj):
        # group candidacies by their position label
        qs = Candidate.objects.filter(**{cand_elec_fk_name: obj})
        buckets = {}
        for c in qs:
            label = getattr(c, position_label_field, "") or "Unspecified"
            buckets.setdefault(label, []).append(c)
        # turn into serializable blocks
        blocks = []
        for label, candidacies in buckets.items():
            blocks.append({
                "id": label,           # use the label as the stable id
                "title": label,
                "candidates": candidacies,
            })
        return PositionBlockSerializer(blocks, many=True).data

# ---- vote payloads (candidate-centric) ----
# Accept either:
#   {"choices":[{"candidate_id": 5}, {"candidate_id": 9}]}
# or legacy shape with a "position" string included.
class BallotChoiceIn(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    position = serializers.CharField(required=False, allow_blank=True)

class BallotInSerializer(serializers.Serializer):
    choices = BallotChoiceIn(many=True)

class BallotOutChoice(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    position = serializers.CharField()

class BallotOutSerializer(serializers.Serializer):
    choices = BallotOutChoice(many=True)

# Results
class ResultsTotalsSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    count = serializers.IntegerField()

class PositionResultsSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    totals = ResultsTotalsSerializer(many=True)

class ElectionResultsSerializer(serializers.Serializer):
    positions = PositionResultsSerializer(many=True)

# --- Admin candidacy write serializers ---
class CandidacyCreateSerializer(serializers.Serializer):
    member_id = serializers.IntegerField(required=False)
    email = serializers.EmailField(required=False)
    name = serializers.CharField(required=False, allow_blank=True)
    position_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        if not data.get("member_id") and not data.get("email"):
            raise serializers.ValidationError("Provide member_id or email+name.")
        return data

class CandidacyPatchSerializer(serializers.Serializer):
    position_id = serializers.IntegerField(required=False, allow_null=True)
    candidacyStatus = serializers.BooleanField(required=False)
    credentials = serializers.CharField(required=False, allow_blank=True)
