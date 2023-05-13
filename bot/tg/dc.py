from dataclasses import dataclass, field
from typing import List, Optional, Type

from marshmallow import EXCLUDE, Schema
import marshmallow_dataclass


# ----------------------------------------------------------------
# bot API objects dataclasses
@dataclass
class User:
    """
    Represents a Telegram user or bot

    Attrs:
        - id: defines user unique identifier
        - is_bot: defines True if user is bot else False
        - first_name: defines user's first name
        - last_name: defines user's last name
        - username: defines user's first username
    """
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str]
    username: Optional[str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class Chat:
    """
    Represents a chat

    Attrs:
        - id: defines chat unique identifier
        - type: defines type of chat (private, group etc)
        - first_name: defines chat's first name
        - last_name: defines chat's last name
        - title: defines title of chat
    """
    id: int
    type: str
    first_name: str
    last_name: Optional[str]
    title: Optional[str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    """
    Represents a message

    Attrs:
        - message_id: defines message unique identifier
        - chat: defines current chat
        - from_: defines user
        - text: defines text of message
    """
    message_id: int
    chat: Chat
    from_: User = field(metadata={'data_key': 'from'})
    text: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Update:
    """
    Represents an incoming update

    Attrs:
        - update_id: defines identifier of current update
        - message: defines message
    """
    update_id: int
    message: Optional[Message]

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    """
    Class for receiving messages from user

    Attrs:
        - ok: True if response is successful else False
        - result: defines result of telegram bot response
    """
    ok: bool
    result: List[Update] = field(default_factory=list)

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    """
    Class for sending messages to user

    Attrs:
        - ok: True if response is successful else False
        - result: defines result of telegram bot response
    """
    ok: bool
    result: Message

    class Meta:
        unknown = EXCLUDE


# ----------------------------------------------------------------
# create schemas entities
GetUpdatesResponseSchema: Type[Schema] = marshmallow_dataclass.class_schema(GetUpdatesResponse)
SendMessageResponseSchema: Type[Schema] = marshmallow_dataclass.class_schema(SendMessageResponse)
