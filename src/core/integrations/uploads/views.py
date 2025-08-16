from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import FileUploadSerializer

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save()
            return Response({
                "status": "success",
                "code": 201,
                "data": saved_data,
                "message": "파일 업로드 성공"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "error",
                "code": 400,
                "message": "유효하지 않은 요청입니다.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)