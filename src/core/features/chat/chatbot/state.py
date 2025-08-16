from enum import Enum

class ChatState(str, Enum):
    IDLE = "idle"
    AWAITING_DESCRIPTION = "awaiting_description"
    OTHER = "other"