from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ClassificationSerializer
from ...core.common.error.error import ImageClassificationError

class ClassificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ClassificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                classified_data = serializer.save()
                return Response({
                    "status": "success",
                    "code": 200,
                    "data": classified_data,
                    "message": "이미지 분류 성공"
                }, status=status.HTTP_200_OK)
            except ImageClassificationError as e:
                return Response({
                    "status": "error",
                    "code": 500,
                    "message": f"이미지 분류 중 오류가 발생했습니다: {e}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({
                    "status": "error",
                    "code": 500,
                    "message": f"서버 오류가 발생했습니다: {e}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "error",
                "code": 400,
                "message": "유효하지 않은 요청입니다.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)