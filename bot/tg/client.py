import requests
from marshmallow import ValidationError

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse, GetUpdatesResponseSchema, SendMessageResponseSchema


# ----------------------------------------------------------------
# telegram client class
class TgClient:
    def __init__(self, token):
        self.__token = token

    @property
    def token(self):
        """
        Getter for the token
        """
        return self.__token

    def get_url(self, method: str) -> str:
        """
        Method to define url

        Params:
            - method: define method of action - send message or get updates

        Returns:
            - string with ready-to-use url
        """
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        """
        Client method to get updates by long polling

        Params:
            - offset: defines identifier of the first update to be returned
            - timeout: defines timeout in seconds for long polling

        Returns:
            - GetUpdatesResponse: bot get message from user
        """
        url: str = self.get_url(method='getUpdates')
        params: dict[str, int] = {'offset': offset, 'timeout': timeout}
        response = requests.get(url, params=params).json()
        return GetUpdatesResponseSchema().load(response)

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        """
        Client method to send a message to user

        Params:
            - chat_id: defines identifier of current chat
            - text: defines text of message

        Returns:
            - SendMessageResponse: bot send message to user
        """
        url: str = self.get_url(method='sendMessage')
        data: dict[str, int | str] = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, json=data).json()
        try:
            return SendMessageResponseSchema().load(response)
        except ValidationError:
            return response
