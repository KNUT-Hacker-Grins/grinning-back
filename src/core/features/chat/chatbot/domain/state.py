from enum import Enum

class ChatState(str, Enum):
    """
    IDLE: 아무 동작도 하지 않고 대기하는 상태
    AWAITING_DESCRIPTION: 유저가 물건(또는 사건 등)에 대한 설명을 입력하기를 기다리는 상태
    OTHER : 정의된 정상 플로우(IDLE, AWAITING_DESCRIPTION 등) 이외의 상태
    """
    IDLE = "idle" 
    AWAITING_DESCRIPTION = "awaiting_description" 
    OTHER = "other"

