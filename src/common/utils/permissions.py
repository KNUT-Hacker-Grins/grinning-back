from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    관리자 권한 확인 (is_staff=True)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff