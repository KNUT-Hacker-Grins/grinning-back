from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.found_items.models import FoundItem

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
