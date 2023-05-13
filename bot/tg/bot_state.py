from typing import Tuple, Optional, Any

from django.db.models import QuerySet
from django.utils.crypto import get_random_string

from bot.models import TgUser
from bot.tg.base_state import BaseState
from goals.models.category import GoalCategory
from goals.models.goal import Goal


# ----------------------------------------------------------------
class BotState1(BaseState):
    """State 1. Start state"""

    def doSomething(self, **kwargs) -> None:
        """
        Action method for bot: do some logic, then set next state

        Params:
            - kwargs: named (keyword) arguments
        """
        item: Any | None = kwargs.get('item')
        if item:
            if item.message.text == '/start':
                tg_user, created = self._check_user(item.message)
                if created:
                    self._send_message(state='success', item=item)
                    self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
                    self.botSession.doSomething(**kwargs)
                elif tg_user.status == TgUser.Status.verified:
                    self._send_message(state='state1-state3', item=item)
                    self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
                else:
                    self._send_message(state='state1-state2', item=item)
                    self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
                    self.botSession.doSomething(**kwargs)
            else:
                self._send_message(state='error', item=item)

    def _check_user(self, message) -> Tuple[TgUser, bool]:
        """
        Method to check user existence.

        Params:
            - message: message with next data - user, text, chat, date

        Returns:
            - Return tuple with user and boolean flag - True if user created, False if user exists
        """
        tg_user, created = self.botSession.dao.get_or_create_user(message)
        return tg_user, created

    def _message_data(self, **kwargs) -> Optional[str]:
        """
        Method to define message data

        Params:
            - kwargs: named (keyword) arguments

        Returns:
            - text for message from bot or None in case of no info about bot state
        """
        message: dict[str, str] = {
            'success': 'Приветствую в телеграм боте TODOList! Ожидайте ваш код верификации!',
            'error': 'Для начала работы воспользуйтесь командой /start',
            'state1-state3': 'Введите команду "/goals" для вывода ваших целей или команду /create для создания цели',
            'state1-state2': 'Введите команду "/check_verification" для проверки статуса верификации бота'
        }
        state: Any | None = kwargs.get('state')
        if state:
            return message.get(state)
        return None

    def _send_message(self, **kwargs) -> None:
        """
        Method to send a message by telegram client

        Params:
            - kwargs: named (keyword) arguments
        """
        text: Optional[str] = self._message_data(state=kwargs.get('state'))
        item: Any | None = kwargs.get('item')
        if item:
            self.client.send_message(chat_id=item.message.chat.id, text=text)


# ----------------------------------------------------------------
class BotState2(BaseState):
    """State 2. Wait verification"""

    def doSomething(self, **kwargs) -> None:
        """
        Action method for bot: do some logic, then set next state

        Params:
            - kwargs: named (keyword) arguments
        """
        item: Any | None = kwargs.get('item')
        try:
            if item:
                tg_user: TgUser = self.botSession.dao.get_user_or_exception(item.message)
                code: str = get_random_string(length=10)
                if item.message.text == '/check_verification':
                    if tg_user and tg_user.status == TgUser.Status.verified:
                        self._send_message(state='verified', item=item)
                        self._send_message(state='state2-state3', item=item)
                        self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
                    else:
                        self._send_message(state='nonverified', item=item, code=code)
                        self._update_user(tg_user, code)
                elif tg_user and tg_user.status != TgUser.Status.verified:
                    self._send_message(state='send_code', item=item, code=code)
                    self._update_user(tg_user, code)
        except TgUser.DoesNotExist:
            self._send_message(state='start', item=item)
            self.botSession.setState(BotState1(client=self.client, botSession=self.botSession))

    @staticmethod
    def _update_user(tg_user: TgUser, code: str) -> None:
        """
        Method to write verification code in users entity

        Params:
            - tg_user: telegram user
            - code: string of verification code
        """
        tg_user.verification_code = code
        tg_user.save(update_fields=('verification_code',))

    def _message_data(self, **kwargs) -> Optional[str]:
        """
        Method to define message data

        Params:
            - kwargs: named (keyword) arguments

        Returns:
            - text for message from bot or None in case of no info about bot state
        """
        message: dict[str, str] = {
            'verified': 'Вы успешно верифицировали бота',
            'nonverified': f"Бот не прошел верификацию, ваш код: {kwargs.get('code')}",
            'send_code': f"Ваш код верификации: {kwargs.get('code')}.\n"
                         f"Введите ваш код в поле 'Верифицировать бота' на сайте",
            'state2-state3': 'Введите команду "/goals" для вывода ваших целей '
                             'или команду "/create" для создания цели',
            'start': 'Для начала работы воспользуйтесь командой "/start"'
        }
        state: Any | None = kwargs.get('state')
        if state:
            return message.get(state)
        return None

    def _send_message(self, **kwargs) -> None:
        """
        Method to send a message by telegram client

        Params:
            - kwargs: named (keyword) arguments
        """
        text: Optional[str] = self._message_data(state=kwargs.get('state'), code=kwargs.get('code'))
        item: Any | None = kwargs.get('item')
        if item:
            self.client.send_message(chat_id=item.message.chat.id, text=text)


# ----------------------------------------------------------------
class BotState3(BaseState):
    """State 3. Bot verified"""

    def doSomething(self, **kwargs) -> None:
        """
        Action method for bot: do some logic, then set next state

        Params:
            - kwargs: named (keyword) arguments
        """
        item: Any | None = kwargs.get('item')
        try:
            if item:
                tg_user: TgUser = self.botSession.dao.get_user_or_exception(item.message)
                if tg_user and tg_user.status == TgUser.Status.verified:
                    if item.message.text == '/goals':
                        goals: str | None = self._get_goals(tg_user)
                        if goals:
                            self._send_message(state='goals', item=item, goals=goals)
                        else:
                            self._send_message(state='empty_goals', item=item)
                    elif item.message.text == '/create':
                        categories: str | None = self._get_categories(tg_user)
                        if categories:
                            self._send_message(state='categories', item=item, categories=categories)
                            self.botSession.setState(BotState4(client=self.client, botSession=self.botSession))
                        else:
                            self._send_message(state='empty_cats', item=item)
                    else:
                        self._send_message(state='error', item=item)
                else:
                    self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
                    self._send_message(state='state3-state2', item=item)
        except TgUser.DoesNotExist:
            self.botSession.setState(BotState1(client=self.client, botSession=self.botSession))
            self._send_message(state='state3-state1', item=item)

    def _get_goals(self, tg_user) -> str | None:
        """
        Method to get all users goals. Return string if goals exist, else None

        Params:
            - tg_user: telegram user

        Returns:
            - string with titles of goals from database or None in case of no goals
        """
        goals: QuerySet[Goal] = self.botSession.dao.get_goals(tg_user)
        if goals:
            return '\n'.join(goal.title for goal in goals)
        else:
            return None

    def _get_categories(self, tg_user) -> str | None:
        """
        Method to get all users categories. Return string if categories exist, else None

        Params:
            - tg_user: telegram user

        Returns:
            - string with titles of categories from database or None in case of no categories
        """
        categories: QuerySet[GoalCategory] = self.botSession.dao.get_categories(tg_user)
        if categories:
            return '\n'.join(category.title for category in categories)
        else:
            return None

    def _message_data(self, **kwargs) -> Optional[str]:
        """
        Method to define message data

        Params:
            - kwargs: named (keyword) arguments

        Returns:
            - text for message from bot or None in case of no info about bot state
        """
        message: dict[str, str] = {
            'empty_goals': 'Вы еще не создавали цели',
            'empty_cats': 'Вы еще не создавали категории',
            'goals': f"Ваши цели:\n"
                     f"{kwargs.get('goals')}",
            'categories': f"Для создания цели выберите одну из ваших категорий:\n"
                          f"{kwargs.get('categories')}",
            'error': 'Неизвестная команда',
            'state3-state2': 'Введите команду "/check_verification" для проверки статуса верификации бота',
            'state3-state1': 'Для начала работы воспользуйтесь командой "/start"'
        }
        state: Any | None = kwargs.get('state')
        if state:
            return message.get(state)
        return None

    def _send_message(self, **kwargs) -> None:
        """
        Method to send a message by telegram client

        Params:
            - kwargs: named (keyword) arguments
        """
        text: Optional[str] = self._message_data(
            state=kwargs.get('state'),
            goals=kwargs.get('goals'),
            categories=kwargs.get('categories')
        )
        item: Any | None = kwargs.get('item')
        if item:
            self.client.send_message(chat_id=item.message.chat.id, text=text)


# ----------------------------------------------------------------
# BotState4
class BotState4(BaseState):
    """State 4. Send categories, wait goal title"""

    def doSomething(self, **kwargs) -> None:
        """
        Action method for bot: do some logic, then set next state

        Params:
            - kwargs: named (keyword) arguments
        """
        item: Any | None = kwargs.get('item')
        try:
            if item:
                tg_user: TgUser = self.botSession.dao.get_user_or_exception(item.message)
                if tg_user and tg_user.status == TgUser.Status.verified:
                    categories: str | None = self._get_categories(tg_user)
                    if categories:
                        categories_list: list[str] = categories.split('\n')
                        if item.message.text == '/cancel':
                            self._send_message(state='cancel', item=item)
                            self._send_message(state='state4-state3', item=item)
                            self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
                        elif item.message.text in categories_list:
                            self._set_category(tg_user, item.message.text)
                            self._send_message(state='create', item=item, category=item.message.text)
                            self.botSession.setState(BotState5(client=self.client, botSession=self.botSession))
                        else:
                            self._send_message(state='error', item=item)
                else:
                    self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
                    self._send_message(state='state4-state2', item=item)
        except TgUser.DoesNotExist:
            self.botSession.setState(BotState1(client=self.client, botSession=self.botSession))
            self._send_message(state='state4-state1', item=item)

    def _get_categories(self, tg_user) -> str | None:
        """
        Method to get all users categories. Return string if categories exist, else None

        Params:
            - tg_user: telegram user

        Returns:
            - string with titles of categories from database or None in case of no categories
        """
        categories: QuerySet[GoalCategory] = self.botSession.dao.get_categories(tg_user)
        if categories:
            return '\n'.join(category.title for category in categories)
        else:
            return None

    def _set_category(self, tg_user, category) -> None:
        """
        Method to write category in users entity

        Params:
            - tg_user: telegram user
            - category: chosen category
        """

        self.botSession.dao.set_category(tg_user, category)

    def _message_data(self, **kwargs) -> Optional[str]:
        """
        Method to define message data

        Params:
            - kwargs: named (keyword) arguments

        Returns:
            - text for message from bot or None in case of no info about bot state
        """
        message: dict[str, str] = {
            'create': f"Для категории {kwargs.get('category')} введите название цели, которую хотите создать",
            'cancel': 'Операция отменена',
            'error': 'Неизвестная команда',
            'empty': 'Вы еще не создавали категорий',
            'state4-state3': 'Введите команду "/goals" для вывода ваших целей '
                             'или команду "/create" для создания цели',
            'state4-state2': 'Введите команду "/check_verification" для проверки статуса верификации бота',
            'state4-state1': 'Для начала работы воспользуйтесь командой "/start"'
        }
        state: Any | None = kwargs.get('state')
        if state:
            return message.get(state)
        return None

    def _send_message(self, **kwargs) -> None:
        """
        Method to send a message by telegram client

        Params:
            - kwargs: named (keyword) arguments
        """
        text: Optional[str] = self._message_data(
            state=kwargs.get('state'),
            categories=kwargs.get('categories'),
            category=kwargs.get('category')
        )
        item: Any | None = kwargs.get('item')
        if item:
            self.client.send_message(chat_id=item.message.chat.id, text=text)


# ----------------------------------------------------------------
# BotState5
class BotState5(BaseState):
    """State 5. Create object"""

    def doSomething(self, **kwargs) -> None:
        """
        Action method for bot: do some logic, then set next state

        Params:
            - kwargs: named (keyword) arguments
        """
        item: Any | None = kwargs.get('item')
        try:
            if item:
                tg_user: TgUser = self.botSession.dao.get_user_or_exception(item.message)
                if tg_user and tg_user.status == TgUser.Status.not_verified:
                    self._send_message(state='state5-state2', item=item)
                    self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
                if tg_user and tg_user.status == TgUser.Status.verified and not tg_user.selected_category:
                    self._send_message(state='state5-state3', item=item)
                    self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
                elif tg_user and tg_user.status == TgUser.Status.verified and tg_user.selected_category:
                    if item.message.text == '/cancel':
                        self._send_message(state='cancel', item=item)
                        self._send_message(state='state5-state3', item=item)
                        self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
                    else:
                        board_id, category_id, goal_id = self._create_goal(tg_user, item)
                        self._send_message(
                            state='success',
                            item=item,
                            category_id=category_id,
                            board_id=board_id,
                            goal_id=goal_id
                        )
                        self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
                        self._send_message(state='state5-state3', item=item)
        except TgUser.DoesNotExist:
            self._send_message(state='state5-state1', item=item)
            self.botSession.setState(BotState1(client=self.client, botSession=self.botSession))

    def _create_goal(self, tg_user, item) -> tuple[int, int, int]:
        """
        Method to create new goal. Return tuple with 3 parameters - board_id, category_id, goal_id

        Params:
            - kwargs: named (keyword) arguments

        Returns:
            - tuple with board id, category id, goal id
        """
        return self.botSession.dao.create_goal(tg_user, item)

    def _message_data(self, **kwargs) -> Optional[str]:
        """
        Method to define message data

        Params:
            - kwargs: named (keyword) arguments

        Returns:
            - text for message from bot or None in case of no info about bot state
        """
        message: dict[str, str] = {
            'cancel': 'Операция отменена',
            'success': f"Ваша цель создана\n"
                       f"mrodionov.fun/boards/{kwargs.get('board_id')}"
                       f"/categories/{kwargs.get('category_id')}"
                       f"/goals?goal={kwargs.get('goal_id')}",
            'state5-state3': 'Введите команду "/goals" для вывода ваших целей '
                             'или команду "/create" для создания цели',
            'state5-state2': 'Введите команду "/check_verification" для проверки статуса верификации бота',
            'state5-state1': 'Для начала работы воспользуйтесь командой "/start"'
        }
        state: Any | None = kwargs.get('state')
        if state:
            return message.get(state)
        return None

    def _send_message(self, **kwargs) -> None:
        """
        Method to send a message by telegram client

        Params:
            - kwargs: named (keyword) arguments
        """
        text: Optional[str] = self._message_data(
            state=kwargs.get('state'),
            category_id=kwargs.get('category_id'),
            board_id=kwargs.get('board_id'),
            goal_id=kwargs.get('goal_id')
        )
        item: Any | None = kwargs.get('item')
        if item:
            self.client.send_message(chat_id=item.message.chat.id, text=text)
