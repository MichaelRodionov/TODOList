import requests

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse, GetUpdatesResponseSchema, SendMessageResponseSchema


# ----------------------------------------------------------------
# telegram client class
class TgClient:
    def __init__(self, token):
        self.__token = token

    @property
    def token(self):
        """Getter for the token"""
        return self.__token

    def get_url(self, method: str) -> str:
        """Method to form url"""
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def make_url(self, method: str) -> str:
        """Method to define a URL"""
        url: str = self.get_url(method)
        return url

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        """Client method to get updates by long polling"""
        url = self.make_url(method='getUpdates')
        params = {'offset': offset, 'timeout': timeout}
        response = requests.get(url, params=params).json()
        return GetUpdatesResponseSchema().load(response)

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        """Client method to send a message to user"""
        url = self.make_url(method='sendMessage')
        data = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, json=data).json()
        return SendMessageResponseSchema().load(response)
