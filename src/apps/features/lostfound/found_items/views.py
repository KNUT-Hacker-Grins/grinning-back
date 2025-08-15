from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from apps.found_items.models import FoundItem
from apps.found_items.serializers import FoundItemSerializer
from apps.found_items.serializers import FoundItemDetailSerializer
from apps.found_items.utils import get_filtered_found_items

class AdminFoundItemListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        items, total, page, limit = get_filtered_found_items(request)
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
            "message": "관리자 조회 성공"
        }, status=status.HTTP_200_OK)
    
class FoundItemCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = FoundItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 비인증 사용자의 경우 None을 저장
        user = request.user if request.user.is_authenticated else None
        serializer.save(user=user)

        return Response({
            "status": "success",
            "code": 201,
            "data": serializer.data,
            "message": "등록 완료"
        }, status=status.HTTP_201_CREATED)

class FoundItemDeleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, id):
        item = get_object_or_404(FoundItem, id=id)

        # 비인증 사용자이거나 게시글 작성자가 아닌 경우 권한 거부
        if not request.user.is_authenticated or item.user != request.user:
            raise PermissionDenied("본인 게시글만 삭제할 수 있습니다.")

        item.delete()
        return Response({
            "status": "success",
            "code": 200,
            "message": "삭제 완료"
        }, status=status.HTTP_200_OK)

class FoundItemDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        item = get_object_or_404(FoundItem, id=id)
        serializer = FoundItemDetailSerializer(item)
        return Response({
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "조회 성공"
        }, status=status.HTTP_200_OK)
    
class FoundItemListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        items, total, page, limit = get_filtered_found_items(request)
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
    
class FoundItemStatusUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    def patch(self, request, id):
        item = get_object_or_404(FoundItem, id=id)

        new_status = request.data.get('status')
        valid_statuses = [choice[0] for choice in FoundItem.STATUS_CHOICES]

        if new_status not in valid_statuses:
            return Response({
                "status": "error",
                "code": 400,
                "message": f"잘못된 상태입니다. 가능한 값: {valid_statuses}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 비인증 사용자이거나 게시글 작성자가 아닌 경우 권한 거부
        if not request.user.is_authenticated or item.user != request.user:
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

class FoundItemUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request, id):
        item = get_object_or_404(FoundItem, id=id)

        # 비인증 사용자이거나 게시글 작성자가 아닌 경우 권한 거부
        if not request.user.is_authenticated or item.user != request.user:
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


