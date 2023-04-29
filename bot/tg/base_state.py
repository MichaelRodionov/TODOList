from abc import ABC, abstractmethod
from typing import Any


# ----------------------------------------------------------------
# base state abstract class
class BaseState(ABC):
    def __init__(self, client, botSession):
        self._botSession = botSession
        self._client = client

    @property
    def botSession(self) -> Any:
        """Getter for the bot session"""
        return self._botSession

    @botSession.setter
    def botSession(self, botSession) -> None:
        """Setter for the bot session"""
        self._botSession = botSession

    @property
    def client(self) -> Any:
        """Getter for the client"""
        return self._client

    @client.setter
    def client(self, client) -> None:
        """Setter for the client"""
        self._client = client

    @abstractmethod
    def doSomething(self, **kwargs):
        """Abstract action method for bot: do some logic, then set next state"""
        pass

    @abstractmethod
    def _message_data(self, **kwargs):
        """Abstract method to define message data"""
        pass

    @abstractmethod
    def _send_message(self, **kwargs):
        """Abstract method to send a message by client entity"""
        pass
