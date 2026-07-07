import json
from channels.generic.websocket import JsonWebsocketConsumer

class ChatbotConsumer(JsonWebsocketConsumer):
    """
    클라이언트가 ws://.../ws/chatbot/<session_id>/ 로 접속하면
    동일 session_id 유저끼리 그룹 브로드캐스트를 받는다.
    """
    def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.group_name = f"chatbot_{self.session_id}"
        self.channel_layer.group_add(self.group_name, self.channel_name)
        self.accept()
        # 선택: 초기 환영 메시지
        self.send_json({"type": "system", "message": "세션 연결됨", "session_id": self.session_id})

    def disconnect(self, close_code):
        self.channel_layer.group_discard(self.group_name, self.channel_name)

    def chatbot_message(self, event):
        # group_send 로 들어온 메시지를 그대로 전달
        self.send_json(event["payload"])
