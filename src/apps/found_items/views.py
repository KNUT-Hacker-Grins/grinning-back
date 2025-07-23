from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from ..accounts.models import User
from .models import FoundItem
from .serializers import FoundItemSerializer, FoundItemDetailSerializer


class FoundItemCreateView(APIView):
    def post(self, request):
        user = User.objects.first()  # 더미 인증
        serializer = FoundItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response({
            "status": "success",
            "code": 201,
            "data": serializer.data,
            "message": "등록 완료"
        }, status=status.HTTP_201_CREATED)


class FoundItemListView(APIView):
    def get(self, request):
        queryset = FoundItem.objects.all().order_by('-id')
        category = request.query_params.get('category')
        found_location = request.query_params.get('found_location')

        if category:
            queryset = queryset.filter(category=category)
        if found_location:
            queryset = queryset.filter(found_location=found_location)

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

        serializer = FoundItemSerializer(items, many=True)

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


class FoundItemDetailView(APIView):
    def get(self, request, id):
        item = get_object_or_404(FoundItem, id=id)
        serializer = FoundItemDetailSerializer(item)
        return Response({
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "조회 성공"
        }, status=status.HTTP_200_OK)


class FoundItemUpdateView(APIView):
    def put(self, request, id):
        item = get_object_or_404(FoundItem, id=id)
        request.user = User.objects.first()  # 더미 인증

        if not request.user.is_staff and item.user != request.user:
            raise PermissionDenied("본인 게시글만 수정할 수 있습니다.")

        serializer = FoundItemSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "수정 완료"
        }, status=status.HTTP_200_OK)


class FoundItemDeleteView(APIView):
    def delete(self, request, id):
        item = get_object_or_404(FoundItem, id=id)
        request.user = User.objects.first()  # 더미 인증

        if not request.user.is_staff and item.user != request.user:
            raise PermissionDenied("본인 게시글만 삭제할 수 있습니다.")

        item.delete()
        return Response({
            "status": "success",
            "code": 200,
            "message": "삭제 완료"
        }, status=status.HTTP_200_OK)


class FoundItemStatusUpdateView(APIView):
    def patch(self, request, id):
        item = get_object_or_404(FoundItem, id=id)
        request.user = User.objects.first()  # 더미 인증

        new_status = request.data.get('status')
        valid_statuses = [choice[0] for choice in FoundItem.STATUS_CHOICES]

        if new_status not in valid_statuses:
            return Response({
                "status": "error",
                "code": 400,
                "message": f"잘못된 상태입니다. 가능한 값: {valid_statuses}"
            }, status=status.HTTP_400_BAD_REQUEST)

        if item.user != request.user:
            raise PermissionDenied("본인 게시글만 상태 변경할 수 있습니다.")

        item.status = new_status
        item.save()

        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "id": item.id,
                "status": item.status
            },
            "message": "상태 변경 완료"
        }, status=status.HTTP_200_OK)
