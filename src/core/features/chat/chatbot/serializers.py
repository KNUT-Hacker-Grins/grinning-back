from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=False, allow_blank=True)
    intent = serializers.CharField(required=False, allow_blank=True)  # '분실물 찾기' | '분실물 신고' | '기타 문의'
    message = serializers.CharField(required=False, allow_blank=True)

class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.CharField()
    state = serializers.CharField()
    reply = serializers.CharField()
    choices = serializers.ListField(child=serializers.CharField(), required=False)
    recommendations = serializers.ListField(child=serializers.DictField(), required=False)
    data = serializers.DictField(required=False)
