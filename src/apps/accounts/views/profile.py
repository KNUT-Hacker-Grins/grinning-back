from rest_framework.views import APIView # APIView 임포트
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.response import UserResponseSerializer
from apps.lost_items.utils.responses import success_response, error_response
from ..serializers.request import UserProfileUpdateSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        내 정보 조회 API
        GET /api/users/me
        """
        try:
            user = request.user
            serializer = UserResponseSerializer(user)
            return success_response(
                data=serializer.data,
                message="조회 성공"
            )
        except Exception as e:
            return error_response(
                error="사용자 정보 조회 중 오류가 발생했습니다.",
                code=500
            )

    def put(self, request):
        """
        내 정보 수정 API (PUT)
        PUT /api/users/me
        """
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data) # partial=False (PUT은 전체 업데이트)
        if not serializer.is_valid():
            return error_response(
                error="입력 데이터가 올바르지 않습니다.",
                code=400,
                details=serializer.errors
            )
        try:
            updated_user = serializer.save()
            return success_response(
                data=UserResponseSerializer(updated_user).data,
                message="프로필 수정 성공"
            )
        except Exception as e:
            return error_response(
                error=f"프로필 수정 중 오류가 발생했습니다: {str(e)}",
                code=500
            )

    def patch(self, request):
        """
        내 정보 부분 수정 API (PATCH)
        PATCH /api/users/me
        """
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True) # partial=True (PATCH는 부분 업데이트)
        if not serializer.is_valid():
            return error_response(
                error="입력 데이터가 올바르지 않습니다.",
                code=400,
                details=serializer.errors
            )
        try:
            updated_user = serializer.save()
            return success_response(
                data=UserResponseSerializer(updated_user).data,
                message="프로필 수정 성공"
            )
        except Exception as e:
            return error_response(
                error=f"프로필 수정 중 오류가 발생했습니다: {str(e)}",
                code=500
            )

    def delete(self, request):
        """
        내 계정 삭제 API
        DELETE /api/users/me
        """
        user = request.user # 현재 로그인한 사용자

        try:
            user.delete()
            return success_response(
                message="계정 삭제 성공",
                code=200
            )
        except Exception as e:
            return error_response(
                error=f"계정 삭제 중 오류가 발생했습니다: {str(e)}",
                code=500
            )