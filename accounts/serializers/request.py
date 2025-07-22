from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    """소셜 로그인 요청용 시리얼라이저"""

    provider = serializers.ChoiceField(choices=['kakao', 'google'])
    code = serializers.CharField(max_length=500)

    def validate_provider(self, value):
        """제공자 검증"""
        if value not in ['kakao', 'google']:
            raise serializers.ValidationError("지원하지 않는 소셜 로그인 제공자입니다.")
        return value

    def validate_code(self, value):
        """인증 코드 검증"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("인증 코드가 필요합니다.")
        return value