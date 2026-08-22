from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response
    detail = response.data
    response.data = {
        "success": False,
        "message": "Validation failed" if response.status_code == 400 else "Request failed",
        "errors": detail,
    }
    return response
