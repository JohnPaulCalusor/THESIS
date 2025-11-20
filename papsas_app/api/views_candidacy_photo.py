# papsas_app/api/views_candidacy_photo.py
from django.apps import apps
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

Candidacy = apps.get_model("papsas_app", "Candidacy")


class CandidacyPhotoUploadView(APIView):
    """
    Upload a photo for a candidacy's linked candidate user.

    POST /api/candidacies/<pk>/photo
    Body (multipart/form-data):
      - photo: image file
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]

    def post(self, request, pk: int):
        try:
            candidacy = (
                Candidacy.objects
                .select_related("candidate")
                .get(pk=pk)
            )
        except Candidacy.DoesNotExist:
            return Response({"detail": "Candidacy not found."}, status=404)

        candidate = getattr(candidacy, "candidate", None)
        if candidate is None:
            return Response(
                {"detail": "This candidacy is not linked to a candidate user."},
                status=400,
            )

        file_obj = request.FILES.get("photo")
        if not file_obj:
            return Response(
                {"detail": "No file received under field 'photo'."},
                status=400,
            )

        # Assumes your User model has an ImageField/FileField named profilePic
        candidate.profilePic = file_obj
        candidate.save(update_fields=["profilePic"])

        try:
            url = candidate.profilePic.url
            full_url = request.build_absolute_uri(url)
        except Exception:
            full_url = None

        return Response({"photoUrl": full_url}, status=200)
