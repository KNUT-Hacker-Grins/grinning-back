from rest_framework import serializers
from .models import LostItem

class LostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostItem
        fields = [
            'lost_item_id',
            'user',
            'title',
            'description',
            'found_at',
            'location',
            'image_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['lost_item_id', 'created_at', 'updated_at', 'user']