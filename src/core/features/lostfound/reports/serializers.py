from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    # 클라이언트에서 입력받을 필드
    post_type = serializers.CharField(write_only=True)
    post_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Report
        fields = ['id', 'post_type', 'post_id', 'reason', 'description', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate(self, data):
        post_type = data.get('post_type')
        post_id = data.get('post_id')

        try:
            content_type = ContentType.objects.get(model=post_type)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({
                'post_type': '유효하지 않은 post_type입니다. (예: founditem, lostitem)'
            })

        model_class = content_type.model_class()
        try:
            post = model_class.objects.get(id=post_id)
        except model_class.DoesNotExist:
            raise serializers.ValidationError({
                'post_id': '해당 게시글이 존재하지 않습니다.'
            })

        # content_type과 object_id를 validated_data에 삽입 (create에서 사용하기 위함)
        data['content_type'] = content_type
        data['object_id'] = post_id
        return data

    def create(self, validated_data):
        validated_data.pop('post_type')
        validated_data.pop('post_id')
        user = self.context['request'].user

        return Report.objects.create(
            user=user,
            **validated_data
        )