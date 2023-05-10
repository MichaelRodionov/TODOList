from typing import Any

from bot.tg.bot_dao import BotDAO
from bot.tg.bot_state import BotState1
from bot.tg.client import TgClient
from todolist.settings import TG_BOT_KEY


# ----------------------------------------------------------------
# bot session class
class BotSession:
    """
    Class representing session with bot

    Attrs:
        - _state: defines current state of bot
        - client: defines connection between telegram user and bot
        - dao: defines data access object to make queries to database
    """
    _state = None
    client: TgClient = TgClient(TG_BOT_KEY)
    dao: BotDAO = BotDAO()

    def __init__(self) -> None:
        self.setState(BotState1(client=self.client, botSession=self))

    def setState(self, state) -> None:
        """
        Method to set state and bot_session
        """
        self._state = state
        self._state.botSession = self

    def doSomething(self, **kwargs) -> Any:
        """
        Action method for bot: do some logic, then set next state

        Attrs:
            - kwargs: named (keyword) arguments

        Returns:
            - result of bot action
        """
        return self._state.doSomething(**kwargs)  # type: ignore

    def run_bot(self) -> None:
        """
        Method to run telegram bot
        """
        update_id: int = 0
        while True:
            print(self._state.__doc__)
            updates = self.client.get_updates(update_id)
            if updates.result:
                for item in updates.result:
                    update_id = item.update_id + 1
                    self.doSomething(item=item)
