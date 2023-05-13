from typing import Type

import factory

from core.models import User
from goals.models.board import Board, BoardParticipant
from goals.models.category import GoalCategory
from goals.models.comment import Comment
from goals.models.goal import Goal


# ----------------------------------------------------------------
# abstract factory
class AbstractFactory(factory.django.DjangoModelFactory):
    title: factory.Sequence = factory.Sequence(lambda x: f"board_{x}")


# ----------------------------------------------------------------
# user factory to create user entities
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model: Type[User] = User

    username: factory.Faker = factory.Faker('user_name')
    password: factory.Faker = factory.Faker('password')


# ----------------------------------------------------------------
# board factory to create board entities
class BoardFactory(AbstractFactory):
    class Meta:
        model: Type[Board] = Board


# ----------------------------------------------------------------
# board_participant factory to create board_participant entities
class BoardParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model: Type[BoardParticipant] = BoardParticipant

    board: factory.SubFactory = factory.SubFactory(BoardFactory)


# ----------------------------------------------------------------
# category factory to create category entities
class CategoryFactory(AbstractFactory):
    class Meta:
        model: Type[GoalCategory] = GoalCategory

    board: factory.SubFactory = factory.SubFactory(BoardFactory)


# ----------------------------------------------------------------
# goal factory to create goal entities
class GoalFactory(AbstractFactory):
    class Meta:
        model: Type[Goal] = Goal

    category: factory.SubFactory = factory.SubFactory(CategoryFactory)


# ----------------------------------------------------------------
# comment factory to create comment entities
class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model: Type[Comment] = Comment

    text: factory.Sequence = factory.Sequence(lambda x: f"testComment_{x}")
    goal: factory.SubFactory = factory.SubFactory(GoalFactory)
