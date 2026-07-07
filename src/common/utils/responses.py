# lost_items/utils/responses.py
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="", code=200, status_code=None):
    """
    성공 응답 공통 함수
    """
    if status_code is None:
        status_code = code

    response_data = {
        "status": "success",
        "code": code,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

    if data is not None:
        response_data["data"] = data

    return Response(response_data, status=status_code)


def error_response(error, code=400, details=None, status_code=None):
    """
    에러 응답 공통 함수
    """
    if status_code is None:
        if code == 400:
            status_code = status.HTTP_400_BAD_REQUEST
        elif code == 401:
            status_code = status.HTTP_401_UNAUTHORIZED
        elif code == 403:
            status_code = status.HTTP_403_FORBIDDEN
        elif code == 404:
            status_code = status.HTTP_404_NOT_FOUND
        elif code == 500:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            status_code = code

    response_data = {
        "status": "error",
        "code": code,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }

    if details is not None:
        response_data["details"] = details

    return Response(response_data, status=status_code)