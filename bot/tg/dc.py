from dataclasses import dataclass, field
from typing import List, Optional

from marshmallow import EXCLUDE
import marshmallow_dataclass


# ----------------------------------------------------------------
# bot API objects dataclasses
@dataclass
class User:
    """Represents a Telegram user or bot"""
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str]
    username: Optional[str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class Chat:
    """Represents a chat"""
    id: int
    type: str
    first_name: str
    last_name: Optional[str]
    title: Optional[str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    """Represents a message"""
    message_id: int
    date: int
    chat: Chat
    from_: User = field(metadata={'data_key': 'from'})
    text: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Update:
    """Represents an incoming update"""
    update_id: int
    message: Optional[Message]

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    """Class for receiving messages from user"""
    ok: bool
    result: List[Update] = field(default_factory=list)

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    """Class for sending messages to user"""
    ok: bool
    result: Message

    class Meta:
        unknown = EXCLUDE


GetUpdatesResponseSchema = marshmallow_dataclass.class_schema(GetUpdatesResponse)
SendMessageResponseSchema = marshmallow_dataclass.class_schema(SendMessageResponse)
