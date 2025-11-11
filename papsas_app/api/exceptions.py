from rest_framework import status
from rest_framework.exceptions import APIException, NotAuthenticated
from rest_framework.views import exception_handler as drf_handler


def api_exception_handler(exc, context):
    resp = drf_handler(exc, context)
    if resp is None:
        return resp

    detail = resp.data.get("detail") if isinstance(resp.data, dict) else None

    if isinstance(exc, NotAuthenticated):
        code = "AUTH_REQUIRED"
        message = detail or "Authentication credentials were not provided."
    else:
        code = getattr(exc, "default_code", "error")
        message = detail or getattr(exc, "detail", "An error occurred.")

    resp.data = {"code": str(code).upper(), "message": str(message)}
    return resp


class APIError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "bad_request"
    default_detail = "Request could not be processed."
