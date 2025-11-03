from enum import StrEnum


class MessageType(StrEnum):
    SENT_MSG_FROM_WORKER = "sent_message_from_worker"
    SENT_MSG_FROM_LAZY = "sent_message_from_lazy"
    REJECTED_MSG = "rejected_msg"
