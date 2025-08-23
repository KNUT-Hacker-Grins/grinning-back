from rest_framework import serializers
from .models import PoliceFoundItem, PoliceLostItem

class PoliceFoundItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceFoundItem
        fields = '__all__'


class PoliceLostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceLostItem
        fields = '__all__'
