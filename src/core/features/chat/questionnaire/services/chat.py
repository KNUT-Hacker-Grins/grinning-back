import uuid
from ..models import Questionnaire

class ChatService:
    @staticmethod
    def create_room_for_questionnaire(q: Questionnaire) -> str:
        # 실제 채팅방 생성 로직으로 교체 (예: ChatRoom.objects.create(...).id)
        return str(uuid.uuid4())
