from typing import Tuple

from django.utils.crypto import get_random_string

from bot.models import TgUser
from bot.tg.base_state import BaseState
from goals.models.category import GoalCategory
from goals.models.goal import Goal


# ----------------------------------------------------------------
# bot states
class BotState1(BaseState):
    """State 1. Start state"""

    def doSomething(self, **kwargs) -> None:
        item = kwargs.get('item')
        if item.message.text == '/start':
            tg_user, created = self._check_user(item.message)
            if created:
                self.send_message(state='success', item=item)
                self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
                self.botSession.doSomething(**kwargs)
            elif tg_user.status == TgUser.Status.verified:
                self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
            else:
                self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
                self.botSession.doSomething(**kwargs)
        else:
            self.send_message(state='error', item=item)

    @staticmethod
    def _check_user(message) -> Tuple[TgUser, bool]:
        tg_user, created = TgUser.objects.get_or_create(
            tg_user_id=message.from_.id,
            tg_chat_id=message.chat.id
        )
        return tg_user, created

    def message_data(self, **kwargs) -> str:
        message = {
            'success': 'Приветствую в телеграм боте TODOList! Ожидайте ваш код верификации!',
            'error': 'Для начала работы воспользуйтесь командой /start'
        }
        return message.get(kwargs.get('state'))

    def send_message(self, **kwargs) -> None:
        text = self.message_data(state=kwargs.get('state'))
        self.client.send_message(chat_id=kwargs.get('item').message.chat.id, text=text)


class BotState2(BaseState):
    """State 2. Wait verification"""

    def doSomething(self, **kwargs) -> None:
        item = kwargs.get('item')
        try:
            tg_user: TgUser = TgUser.objects.get(tg_user_id=item.message.from_.id)
            code: str = get_random_string(length=10)
            if item.message.text == '/check_verification':
                if tg_user and tg_user.status == TgUser.Status.verified:
                    self.send_message(state='verified', item=item)
                    self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
                else:
                    self.send_message(state='nonverified', item=item, code=code)
                    self.update_user(tg_user, code)
            elif tg_user and tg_user.status != TgUser.Status.verified:
                self.send_message(state='send_code', item=item, code=code)
                self.update_user(tg_user, code)
        except TgUser.DoesNotExist:
            self.botSession.setState(BotState1(client=self.client, botSession=self.botSession))

    @staticmethod
    def update_user(tg_user: TgUser, code: str) -> None:
        tg_user.verification_code = code
        tg_user.save(update_fields=('verification_code',))

    def message_data(self, **kwargs) -> str:
        message = {
            'verified': 'Вы успешно верифицировали бота',
            'nonverified': f"Бот не прошел верификацию, ваш код: {kwargs.get('code')}",
            'send_code': f"Ваш код верификации: {kwargs.get('code')}",
        }
        return message.get(kwargs.get('state'))

    def send_message(self, **kwargs) -> None:
        text = self.message_data(state=kwargs.get('state'), code=kwargs.get('code'))
        self.client.send_message(chat_id=kwargs.get('item').message.chat.id, text=text)


class BotState3(BaseState):
    """State 3. Bot verified"""

    def doSomething(self, **kwargs) -> None:
        item = kwargs.get('item')
        try:
            tg_user: TgUser = TgUser.objects.get(tg_user_id=item.message.from_.id)
            if tg_user and tg_user.status == TgUser.Status.verified:
                if item.message.text == '/goals':
                    goals = self.get_goals(tg_user)
                    if goals:
                        self.send_message(state='goals', item=item, goals=goals)
                    else:
                        self.send_message(state='empty_goals', item=item)
                elif item.message.text == '/create':
                    categories = self.get_categories(tg_user)
                    if categories:
                        self.send_message(state='categories', item=item, categories=categories)
                        self.botSession.setState(BotState4(client=self.client, botSession=self.botSession))
                    elif not categories:
                        self.send_message(state='empty_cats', item=item)
                else:
                    self.send_message(state='error', item=item)
            else:
                self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
        except TgUser.DoesNotExist:
            self.botSession.setState(BotState1(client=self.client, botSession=self.botSession))

    @staticmethod
    def get_goals(tg_user) -> str:
        goals = Goal.objects.select_related('category').filter(
            category__board__participants__user=tg_user.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)
        return '\n'.join(goal.title for goal in goals)

    @staticmethod
    def get_categories(tg_user) -> str | None:
        categories = GoalCategory.objects.select_related('board').filter(
            board__participants__user=tg_user.user,
            board__is_deleted=False,
            is_deleted=False
        )
        if categories:
            return '\n'.join(category.title for category in categories)
        else:
            return None

    def message_data(self, **kwargs) -> str:
        message = {
            'empty_goals': 'Вы еще не создавали цели',
            'empty_cats': 'Вы еще не создавали категории',
            'goals': f"Ваши цели:\n"
                     f"{kwargs.get('goals')}",
            'categories': f"Для создания цели выберите одну из ваших категорий:\n"
                          f"{kwargs.get('categories')}",
            'error': 'Неизвестная команда',
        }
        return message.get(kwargs.get('state'))

    def send_message(self, **kwargs) -> None:
        text = self.message_data(
            state=kwargs.get('state'),
            goals=kwargs.get('goals'),
            categories=kwargs.get('categories')
        )
        self.client.send_message(chat_id=kwargs.get('item').message.chat.id, text=text)


class BotState4(BaseState):
    """State 4. Send categories, wait goal title"""

    def doSomething(self, **kwargs) -> None:
        item = kwargs.get('item')
        try:
            tg_user: TgUser = TgUser.objects.get(tg_user_id=item.message.from_.id)
            if tg_user and tg_user.status == TgUser.Status.verified:
                categories = self.get_categories(tg_user)
                categories_list = categories.split('\n')
                if item.message.text == '/cancel':
                    self.send_message(state='cancel', item=item)
                    self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
                elif item.message.text in categories_list:
                    self.set_category(tg_user, item.message.text)
                    self.send_message(state='create', item=item, category=item.message.text)
                    self.botSession.setState(BotState5(client=self.client, botSession=self.botSession))
                else:
                    self.send_message(state='error', item=item)
            else:
                self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
        except TgUser.DoesNotExist:
            self.botSession.setState(BotState1(client=self.client, botSession=self.botSession))

    @staticmethod
    def get_categories(tg_user) -> str | None:
        categories = GoalCategory.objects.select_related('board').filter(
            board__participants__user=tg_user.user,
            board__is_deleted=False,
            is_deleted=False
        )
        if categories:
            return '\n'.join(category.title for category in categories)
        else:
            return None

    @staticmethod
    def set_category(tg_user, category) -> None:
        category = GoalCategory.objects.select_related('board').get(
            board__participants__user=tg_user.user,
            board__is_deleted=False,
            is_deleted=False,
            title__iexact=category
        )
        tg_user.selected_category = category
        tg_user.save()

    def message_data(self, **kwargs) -> str:
        message = {
            'create': f"Для категории {kwargs.get('category')} введите название цели, которую хотите создать",
            'cancel': 'Операция отменена',
            'error': 'Неизвестная команда',
            'empty': 'Вы еще не создавали категорий'
        }
        return message.get(kwargs.get('state'))

    def send_message(self, **kwargs) -> None:
        text = self.message_data(
            state=kwargs.get('state'),
            categories=kwargs.get('categories'),
            category=kwargs.get('category')
        )
        self.client.send_message(chat_id=kwargs.get('item').message.chat.id, text=text)


class BotState5(BaseState):
    """State 5. Create object"""

    def doSomething(self, **kwargs) -> None:
        item = kwargs.get('item')
        try:
            tg_user = TgUser.objects.get(tg_user_id=item.message.from_.id)
            if tg_user and tg_user.status == TgUser.Status.not_verified:
                self.botSession.setState(BotState2(client=self.client, botSession=self.botSession))
            if tg_user and tg_user.status == TgUser.Status.verified and not tg_user.selected_category:
                self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
            elif tg_user and tg_user.status == TgUser.Status.verified and tg_user.selected_category:
                if item.message.text == '/cancel':
                    self.send_message(state='cancel', item=item)
                    self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
                else:
                    tg_user = TgUser.objects.get(tg_user_id=item.message.from_.id)
                    board_id, category_id, goal_id = self.create_goal(tg_user, item)
                    data = {
                        'board_id': board_id,
                        'category_id': category_id,
                        'goal_id': goal_id
                    }
                    self.send_message(
                        state='success',
                        item=item,
                        category=data
                    )
                    self.botSession.setState(BotState3(client=self.client, botSession=self.botSession))
        except TgUser.DoesNotExist:
            self.botSession.setState(BotState1(client=self.client, botSession=self.botSession))

    @staticmethod
    def create_goal(tg_user, item) -> tuple:
        new_goal = Goal.objects.create(
            user=tg_user.user,
            category=tg_user.selected_category,
            title=item.message.text
        )
        return new_goal.category.board.id, new_goal.category.id, new_goal.id

    def message_data(self, **kwargs) -> str:
        message = {
            'success': f"Ваша цель создана\n"
                       f"mrodionov.fun/boards/{kwargs.get('category').get('board_id')}"
                       f"/categories/{kwargs.get('category').get('board_id')}"
                       f"/goals?goal={kwargs.get('category').get('goal_id')}",
            'cancel': 'Операция отменена'
        }
        return message.get(kwargs.get('state'))

    def send_message(self, **kwargs) -> None:
        text = self.message_data(
            state=kwargs.get('state'),
            category=kwargs.get('category'),
        )
        self.client.send_message(chat_id=kwargs.get('item').message.chat.id, text=text)
