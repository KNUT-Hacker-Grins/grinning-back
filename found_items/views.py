from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from accounts.models import User
from .models import FoundItem
from .serializers import FoundItemSerializer
from .serializers import FoundItemDetailSerializer

class FoundItemViewSet(viewsets.ModelViewSet):
    queryset = FoundItem.objects.all().order_by('-id')
    serializer_class = FoundItemSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  

    """
    User.objects.first()로 DB에 있는 첫 번째 유저(보통 수퍼유저) 를 가져와서
    해당 분실물 객체를 저장할 때 user 필드에 자동으로 넣어줍니다

    perform_create()는 POST 요청으로 새로운 객체를 생성할 때, 
    Django REST Framework가 자동으로 호출하는 훅(hook) 메서드입니다.
    """
    def perform_create(self, serializer):
        user = User.objects.first()  
        serializer.save(user=user)

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "status": "success",
            "code": 201,
            "data": response.data,
            "message": "등록 완료"
        }, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        found_location = self.request.query_params.get('found_location')
        if category:
            queryset = queryset.filter(category=category)
        if found_location:
            queryset = queryset.filter(found_location=found_location)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
        except ValueError:
            page, limit = 1, 10
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        items = queryset[start:end]
        serializer = self.get_serializer(items, many=True)
        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "items": serializer.data,
                "page": page,
                "limit": limit,
                "total": total
            },
            "message": "조회 성공"
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, id=None):
        found_item = get_object_or_404(self.get_queryset(), id=id)
        serializer = self.get_serializer(found_item)
        return Response({
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "조회 성공"
        }, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        # 상세 조회만 detail serializer 사용
        if self.action == 'retrieve':
            return FoundItemDetailSerializer
        return self.serializer_class
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user = User.objects.first() 

        if instance.user != request.user:
            raise PermissionDenied("본인 게시글만 수정할 수 있습니다.")

        # partial=False → PUT 전체 수정
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        """
        사용자가 보낸 데이터를 serializer가 내부 필드 정의에 따라 검증합니다.
        필수 필드 누락, 잘못된 형식, 제한 위반 등을 검사합니다.
        """
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "수정 완료"
        }, status=status.HTTP_200_OK)