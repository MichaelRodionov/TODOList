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
        return self._botSession

    @botSession.setter
    def botSession(self, botSession) -> None:
        self._botSession = botSession

    @property
    def client(self) -> Any:
        return self._client

    @client.setter
    def client(self, client) -> None:
        self._client = client

    @abstractmethod
    def doSomething(self, **kwargs) -> None:
        pass

    @abstractmethod
    def message_data(self, **kwargs) -> str:
        pass

    @abstractmethod
    def send_message(self, **kwargs) -> None:
        pass
