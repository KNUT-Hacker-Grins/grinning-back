from rest_framework import status
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import LostItem
from .serializers import LostItemSerializer
from accounts.models import User

class LostItemCreateView(generics.CreateAPIView):
    queryset = LostItem.objects.all()
    serializer_class = LostItemSerializer
    permission_classes = [permissions.AllowAny]  # MVP 인증 없음

    def perform_create(self, serializer):
        """
        오브젝트(DB 레코드) 생성 로직을 담당.
        → DB에 저장하는 "실제 행위"만 처리.
        """
        # user = self.request.user
        user = User.objects.first()  # DB에 유저 반드시 있어야 함
        serializer.save(user=user)  # 나중에 인증 붙이면 동작함

    def create(self, request, *args, **kwargs):
        """
        전체 POST 요청 처리 플로우를 담당.
        요청 데이터 유효성 검사
        perform_create 호출 (실제 저장)
        응답 객체(Response) 생성
        """
        response = super().create(request, *args, **kwargs)

        data = response.data
        # 필요한 데이터 골라서 응답 객체 만들기 
        # data = {
        #     "id": data["lost_item_id"],
        #     "title": data["title"]
        # }
        
        return Response({
            "status": "success",
            "code": 201,
            "data": data,
            "message": "등록 완료"
        }, status=status.HTTP_201_CREATED)