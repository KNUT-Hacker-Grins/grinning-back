from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def push_step(session_id: str, role: str, message: str, data: dict | None = None):
    """
    role: 'system' | 'bot' | 'user'
    message: 화면에 바로 보여줄 문자열
    data: 부가 데이터(옵션)
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chatbot_{session_id}",
        {
            "type": "chatbot_message",
            "payload": {
                "role": role,
                "message": message,
                "data": data or {},
            },
        },
    )
    