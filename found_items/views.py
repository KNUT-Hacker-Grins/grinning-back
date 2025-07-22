from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import FoundItem
from .serializers import FoundItemSerializer
from accounts.models import User
from django.shortcuts import get_object_or_404
from .models import FoundItem
from .serializers import FoundItemSerializer, FoundItemDetailSerializer
from accounts.models import User

class FoundItemViewSet(viewsets.ModelViewSet):
    queryset = FoundItem.objects.all().order_by('-id')
    serializer_class = FoundItemSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  

    def perform_create(self, serializer):
        user = User.objects.first()  # MVP용 임시
        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        data = response.data
        # data = {
        #     'id': data['id'],
        #     'title' : data['title']
        # }
        return Response({
            "status": "success",
            "code": 201,
            "data": data,
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