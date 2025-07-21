from rest_framework import serializers
from .models import FoundItem

class FoundItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoundItem
        fields = [
            'id',
            'user',
            'title',
            'description',
            'found_at',
            'location',
            'image_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']