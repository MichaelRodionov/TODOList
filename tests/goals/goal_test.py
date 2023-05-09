from typing import Any

import pytest
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import User
from core.serializers import UserDetailSerializer
from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from goals.serializers.goal import GoalSerializer
from tests.factories import BoardParticipantFactory, BoardFactory, CategoryFactory, GoalFactory


# ----------------------------------------------------------------
# goal tests
class TestGoal:
    @pytest.mark.django_db
    def test_create_goal(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Goal create test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 201
            - Response data is not None
            - title field from response == title field from expected_response
            - id field from response == id field from expected_response
            - status field from response == status field from expected_response
            - priority field from response == priority field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(
            board=BoardFactory.create(),
            user=user_auth.get('user')
        )
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        post_response: Any = client.post(
            '/goals/goal/create',
            data={
                "title": "testGoal",
                "category": category.id
            },
            content_type='application/json',
        )
        expected_response: dict[str, None | str | int] = {
            "id": post_response.data.get('id'),
            "category": category.id,
            "created": None,
            "updated": None,
            "title": "testGoal",
            "description": "",
            "status": 1,
            "priority": 2,
            "due_date": None
        }

        assert post_response.status_code == 201, 'Goal was not created successfully'
        assert post_response.data is not None, 'HttpResponseError'
        assert post_response.data.get('title') == expected_response.get('title'), 'Wrong title data'
        assert post_response.data.get('id') == expected_response.get('id'), 'Wrong id'
        assert post_response.data.get('status') != Goal.Status.archived, 'Wrong status'
        assert post_response.data.get('priority') == expected_response.get('priority'), 'Wrong priority expected'

    @pytest.mark.django_db
    def test_create_goal_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Goal create test with role reader

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 403
            - Response data is not None
            - response data == data from expected response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(
            board=BoardFactory.create(),
            user=user_auth.get('user'),
            role=BoardParticipant.Role.reader
        )
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        post_response: Any = client.post(
            '/goals/goal/create',
            data={
                "title": "testGoal",
                "category": category.id
            },
            content_type='application/json',
        )
        expected_response: dict[str, str] = {
            'detail': 'You are allowed only to read, not to create'
        }

        assert post_response.status_code == 403, 'Goal was not created successfully'
        assert post_response.data is not None, 'HttpResponseError'
        assert post_response.data == expected_response

    @pytest.mark.django_db
    def test_retrieve_goal(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Goal retrieve test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 200
            - Response data is not None
            - title field from response == title field from expected_response
            - id field from response == id field from expected_response
            - status field from response == status field from expected_response
            - priority field from response == priority field from expected_response
            - due_date field from response == due_date field from expected_response
            - description field from response == description field from expected_response
            - category field from response == category field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        response: Any = client.get(
            f'/goals/goal/{goal.id}',
        )
        expected_response: dict[str, list[ReturnDict]] = {
            "id": goal.id,
            "user": [
                UserDetailSerializer(user_auth.get('user')).data
            ],
            "created": goal.created,
            "updated": goal.updated,
            "title": goal.title,
            "description": goal.description,
            "status": goal.status,
            "priority": goal.priority,
            "due_date": goal.due_date,
            "category": goal.category.id
        }

        assert response.status_code == 200, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data.get('id') == expected_response.get('id'), 'Wrong id expected'
        assert response.data.get('title') == expected_response.get('title'), 'Wrong title expected'
        assert response.data.get('status') == expected_response.get('status'), 'Wrong status expected'
        assert response.data.get('priority') == expected_response.get('priority'), 'Wrong priority expected'
        assert response.data.get('due_date') == expected_response.get('due_date'), 'Wrong due_date expected'
        assert response.data.get('description') == expected_response.get('description'), 'Wrong description expected'
        assert response.data.get('category') == expected_response.get('category'), 'Wrong category expected'

    @pytest.mark.django_db
    def test_retrieve_goal_403(self, client: Any, user_not_auth: User) -> None:
        """
        Goal retrieve test without authorization

        Params:
            - client: A Django test client instance.
            - user_not_auth: A fixture that create user instance but don't log in

        Checks:
            - Response status code is 403
            - Response data is not None
            - response data == data from expected response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_not_auth)
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_not_auth)
        goal: Any = GoalFactory.create(category=category, user=user_not_auth)
        response: Any = client.get(
            f'/goals/goal/{goal.id}',
        )
        expected_response: dict[str, str] = {
            "detail": 'Authentication credentials were not provided.'
        }

        assert response.status_code == 403, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_goal_list(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Goal list test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 200
            - Response data is not None
            - response data == data from expected response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goals: Any = GoalFactory.create_batch(2, category=category, user=user_auth.get('user'))
        expected_response: list[ReturnDict] = [
            GoalSerializer(goals[0]).data,
            GoalSerializer(goals[1]).data,
        ]
        response: Any = client.get('/goals/goal/list')

        assert response.status_code == 200, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_goal_list_403(self, client: Any, user_not_auth: User) -> None:
        """
        Goal list test without authorization

        Params:
            - client: A Django test client instance.
            - user_not_auth: A fixture that create user instance but don't log in

        Checks:
            - Response status code is 403
            - Response data is not None
            - response data == data from expected response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_not_auth)
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_not_auth)
        GoalFactory.create_batch(2, category=category, user=user_not_auth)
        expected_response: dict[str, str] = {"detail": 'Authentication credentials were not provided.'}
        response: Any = client.get('/goals/goal/list')

        assert response.status_code == 403, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_update_goal(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Goal update test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 200
            - Response data is not None
            - title field from response == title field from expected_response
            - id field from response == id field from expected_response
            - status field from response == status field from expected_response
            - priority field from response == priority field from expected_response
            - description field from response == description field from expected_response
            - category field from response == category field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        expected_response: dict[str, str | list[ReturnDict]] = {
            "id": goal.id,
            "user": [UserDetailSerializer(user_auth.get('user')).data],
            "created": goal.created,
            "updated": goal.updated,
            "title": "testGoal_edited",
            "description": 'testDescription',
            "status": goal.status,
            "priority": goal.priority,
            "due_date": goal.due_date,
            "category": goal.category.id
        }
        put_response: Any = client.put(
            f'/goals/goal/{goal.id}',
            data={
                'title': 'testGoal_edited',
                'category': category.id,
                'description': 'testDescription'
            },
            content_type='application/json',
        )

        assert put_response.status_code == 200, 'Goal was not updated successfully'
        assert put_response.data is not None, 'HttpResponseError'
        assert put_response.data.get('title') == expected_response.get('title'), 'Wrong title data'
        assert put_response.data.get('id') == expected_response.get('id'), 'Wrong id'
        assert put_response.data.get('status') == expected_response.get('status'), 'Wrong status'
        assert put_response.data.get('priority') == expected_response.get('priority'), 'Wrong priority expected'
        assert put_response.data.get('category') == expected_response.get('category'), 'Wrong category expected'
        assert put_response.data.get('description') == expected_response.get(
            'description'), 'Wrong description expected'

    @pytest.mark.django_db
    def test_update_goal_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Goal update test with role reader

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 403
            - Response data is not None
            - response data == data from expected response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(
            user=user_auth.get('user'),
            role=BoardParticipant.Role.reader
        )
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        expected_response: dict[str, str] = {
            'detail': 'You do not have permission to perform this action.'
        }
        put_response: Any = client.put(
            f'/goals/goal/{goal.id}',
            data={
                'title': 'testGoal_edited',
                'category': category.id,
                'description': 'testDescription'
            },
            content_type='application/json',
        )

        assert put_response.status_code == 403, 'Board was edited successfully'
        assert put_response.data is not None, 'HttpResponseError'
        assert put_response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_delete_goal(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Goal delete test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 204
            - Response data is None
            - Goal status field changes to archived

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        delete_response: Any = client.delete(
            f'/goals/goal/{goal.id}',
        )
        deleted_goal: Goal = Goal.objects.get(id=goal.id)

        assert delete_response.status_code == 204, 'Goal was not deleted successfully'
        assert delete_response.data is None, 'HttpResponseError'
        assert deleted_goal.status == Goal.Status.archived, 'Wrong status expected'

    @pytest.mark.django_db
    def test_delete_category_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Goal delete test with role reader

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 403
            - Response data is not None
            - response data == data from expected response
            - Goal status not equal archived

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(
            user=user_auth.get('user'),
            role=BoardParticipant.Role.reader
        )
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        expected_response: dict[str, str] = {
            'detail': 'You do not have permission to perform this action.'
        }
        delete_response: Any = client.delete(
            f'/goals/goal/{goal.id}',
        )
        deleted_goal: Goal = Goal.objects.get(id=goal.id)

        assert delete_response.status_code == 403, 'Category was deleted successfully'
        assert delete_response.data is not None, 'HttpResponseError'
        assert delete_response.data == expected_response, 'Wrong data'
        assert deleted_goal.status != Goal.Status.archived, 'Wrong status expected'
