from dataclasses import dataclass
from typing import Optional, Union

from rest_framework.response import Response

CODES = {
    'NOT_FOUND': 404,
    'FORBIDDEN': 403,
    'ALREADY_EXISTS': 409,
    'HAS_VOTES': 409,
    'VALIDATION_ERROR': 400,
    'EMAIL_TAKEN': 409,
    'ALREADY_REGISTERED': 409,
    'NOT_REGISTERED': 409,
    'RATE_LIMITED': 429,
    'EVENT_NOT_FOUND': 404,
    'EVENT_CLOSED': 400,
    'MEMBER_ONLY': 403,
}

@dataclass(frozen=True)
class ApiError:
    code: str
    message: str

# error_response expects a code string or ApiError so callers can default to shared messages.
EVENT_NOT_FOUND = ApiError("EVENT_NOT_FOUND", "Event not found.")
EVENT_CLOSED = ApiError("EVENT_CLOSED", "Event registration for this event is closed.")
MEMBER_ONLY = ApiError("MEMBER_ONLY", "Only members may register for events.")


def error_response(code: Union[str, ApiError], message: Optional[str] = None):
    if isinstance(code, ApiError):
        error = code
        code_value = error.code
        message_value = error.message
    else:
        code_value = code
        message_value = message or ""
    return Response({"code": code_value, "message": message_value}, status=CODES.get(code_value, 400))
