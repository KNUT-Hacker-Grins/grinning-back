from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from apps.found_items.models import FoundItem
from apps.lost_items.models import LostItem

class MapPostListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Query active found items with location
        found_items = FoundItem.objects.filter(
            status='available',
            latitude__isnull=False,
            longitude__isnull=False
        ).values('id', 'title', 'latitude', 'longitude')

        # Query active lost items with location
        lost_items = LostItem.objects.filter(
            status='searching',
            latitude__isnull=False,
            longitude__isnull=False
        ).values('id', 'title', 'latitude', 'longitude')

        # Add post_type to each dictionary
        found_posts = [{'post_type': 'found', **item} for item in found_items]
        lost_posts = [{'post_type': 'lost', **item} for item in lost_items]

        # Combine the two querysets
        all_posts = found_posts + lost_posts

        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "posts": all_posts
            },
            "message": "지도 게시물 조회 성공"
        }, status=status.HTTP_200_OK)
