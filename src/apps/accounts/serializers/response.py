from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserResponseSerializer(serializers.ModelSerializer):
    """사용자 정보 응답용 시리얼라이저"""

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'date_joined']
        read_only_fields = ['id', 'name', 'email', 'date_joined']

    def to_representation(self, instance):
        """API 명세서에 맞게 필드명 변경"""
        data = super().to_representation(instance)
        # date_joined를 created_at으로 변경
        if 'date_joined' in data:
            data['created_at'] = data.pop('date_joined')
        return data


class LoginResponseSerializer(serializers.Serializer):
    """로그인 응답용 시리얼라이저"""

    access_token = serializers.CharField()
    user = UserResponseSerializer()

    def to_representation(self, instance):
        """로그인 응답 데이터 구성"""
        return {
            'access_token': instance['access_token'],
            'user': UserResponseSerializer(instance['user']).data
        }