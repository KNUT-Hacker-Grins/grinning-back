from rest_framework import serializers
from .models import PoliceFoundItem

class PoliceFoundItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceFoundItem
        fields = '__all__'
