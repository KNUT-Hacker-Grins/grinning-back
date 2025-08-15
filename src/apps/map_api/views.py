from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers

from apps.lost_items.models import LostItem
from apps.found_items.models import FoundItem

class MapItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=100)
    image_url = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    item_type = serializers.CharField(max_length=10) # 'lost' or 'found'

class MapItemsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lost_items = LostItem.objects.filter(latitude__isnull=False, longitude__isnull=False)
        found_items = FoundItem.objects.filter(latitude__isnull=False, longitude__isnull=False)

        combined_items = []

        for item in lost_items:
            combined_items.append({
                'id': item.id,
                'title': item.title,
                'image_url': item.image_urls[0] if item.image_urls else None, # Assuming image_urls is a list
                'latitude': item.latitude,
                'longitude': item.longitude,
                'item_type': 'lost'
            })

        for item in found_items:
            combined_items.append({
                'id': item.id,
                'title': item.title,
                'image_url': item.image_urls[0] if item.image_urls else None, # Now using image_urls
                'latitude': item.latitude,
                'longitude': item.longitude,
                'item_type': 'found'
            })
        
        serializer = MapItemSerializer(combined_items, many=True)
        return Response(serializer.data)
