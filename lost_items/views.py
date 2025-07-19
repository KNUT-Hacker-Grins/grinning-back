from rest_framework import generics, permissions
from .models import LostItem
from .serializers import LostItemSerializer
from accounts.models import User

class LostItemCreateView(generics.CreateAPIView):
    queryset = LostItem.objects.all()
    serializer_class = LostItemSerializer
    permission_classes = [permissions.AllowAny]  # MVP 인증 없음

    def perform_create(self, serializer):
        # user = self.request.user
        user = User.objects.first()  # DB에 유저 반드시 있어야 함
        serializer.save(user=user)  # 나중에 인증 붙이면 동작함