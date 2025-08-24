from rest_framework import serializers
from .models import Questionnaire
# Post 모델 경로는 프로젝트에 맞게 수정
from core.features.chat.chat.models import ChatRoom

class DeliverRequestSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=64)
    post_id = serializers.IntegerField(min_value=1)

    def validate_post_id(self, value):
        if not ChatRoom.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 post_id 입니다.")
        return value


class ApproveRequestSerializer(serializers.Serializer):
    questionnaire_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=("approve", "reject"))
    reason = serializers.CharField(allow_blank=True, required=False)

    def validate(self, attrs):
        qid = attrs["questionnaire_id"]
        try:
            q = Questionnaire.objects.get(id=qid)
        except Questionnaire.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 questionnaire_id 입니다.")
        if q.status != Questionnaire.Status.PENDING:
            raise serializers.ValidationError("이미 처리된 질문지입니다.")
        if attrs["action"] == "reject" and not attrs.get("reason"):
            raise serializers.ValidationError("거부 시 reason은 필수입니다.")
        return attrs
