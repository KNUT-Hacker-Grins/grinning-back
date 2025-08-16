from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from core.features.lostfound.lost_items.models import LostItem
from core.common.utils.permissions import IsAdminUser
from core.common.utils.responses import success_response

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_delete_lost_item(request, id):
    """관리자 분실물 신고 강제 삭제 API"""

    # 1. 분실물 조회 (없으면 404)
    lost_item = get_object_or_404(LostItem, id=id)

    # 2. 강제 삭제 (관리자 권한이므로 작성자 확인 불필요)
    lost_item.delete()

    # 3. 성공 응답
    return success_response(
        message="강제 삭제 완료",
        code=200
    )