from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework import status as drf_status
from rest_framework.response import Response
from rest_framework.decorators import action
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
    
        if not request.user.is_staff:
            queryset = queryset.filter(status='available')
        
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
    
   
    def destroy(self, request, *args, **kwargs):
        # 임시 인증 로직: 개발 중이라면 강제로 로그인 유저 지정
        instance = self.get_object()
        request.user = User.objects.first() 

        # 본인 게시글만 삭제 가능
        if instance.user != request.user:
            raise PermissionDenied("본인 게시글만 삭제할 수 있습니다.")

        self.perform_destroy(instance)

        return Response({
            "status": "success",
            "code": 200,
            "message": "삭제 완료"
        }, status=status.HTTP_200_OK)
    
    """이 데코레이터는 DRF ViewSet에 새로운 커스텀 API 엔드포인트를 만들기 위해 꼭 필요합니다."""
    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, id=None):
        instance = self.get_object()
        request.user = User.objects.first() 
        new_status = request.data.get('status')

        # 상태 값 유효성 검사
        valid_statuses = [choice[0] for choice in FoundItem.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({
                "status": "error",
                "code": 400,
                "message": f"잘못된 상태입니다. 가능한 값: {valid_statuses}"
            }, status=drf_status.HTTP_400_BAD_REQUEST)

        # 본인 게시글만 상태 변경 가능
        if instance.user != request.user:
            raise PermissionDenied("본인 게시글만 상태 변경할 수 있습니다.")

        instance.status = new_status
        instance.save()

        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "id": instance.id,
                "status": instance.status
            },
            "message": "상태 변경 완료"
        }, status=drf_status.HTTP_200_OK)