from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']