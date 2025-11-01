from rest_framework.response import Response

CODES = {
    'NOT_FOUND': 404,
    'FORBIDDEN': 403,
    'ALREADY_EXISTS': 409,
    'HAS_VOTES': 409,
    'VALIDATION_ERROR': 400,
    'EMAIL_TAKEN': 409,
}

def error_response(code: str, message: str):
    return Response({"code": code, "message": message}, status=CODES.get(code, 400))
