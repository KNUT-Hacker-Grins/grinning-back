from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from core.common.utils.responses import error_response, success_response
from ..serializers.request import RegisterRequestSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    이메일/비밀번호 기반 사용자 회원가입 API
    POST /api/auth/register
    """
    serializer = RegisterRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            error="입력 데이터가 올바르지 않습니다.",
            code=400,
            details=serializer.errors
        )

    try:
        user = serializer.save()
        return success_response(
            data={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "phone_number": user.phone_number,
                "created_at": user.date_joined.isoformat()
            },
            message="회원가입 성공",
            code=201
        )
    except Exception as e:
        return error_response(
            error=f"회원가입 중 오류가 발생했습니다: {str(e)}",
            code=500
        )
