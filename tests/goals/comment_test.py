from typing import Any

import pytest
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import User
from core.serializers import UserDetailSerializer
from goals.models.board import BoardParticipant
from goals.serializers.comment import CommentSerializer
from tests.factories import BoardParticipantFactory, BoardFactory, CategoryFactory, GoalFactory, CommentFactory


# ----------------------------------------------------------------
# comment tests
class TestComment:
    @pytest.mark.django_db
    def test_create_comment(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Comment create test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 201
            - Response data is not None
            - text field from response == text field from expected_response
            - id field from response == id field from expected_response
            - goal field from response == goal field from expected_response

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
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        post_response: Any = client.post(
            '/goals/goal_comment/create',
            data={
                "text": "testComment",
                "goal": goal.id
            },
            content_type='application/json',
        )
        expected_response: dict[str, int | str | None] = {
            "id": 1,
            "created": None,
            "updated": None,
            "text": "testComment",
            "goal": goal.id
        }

        assert post_response.status_code == 201, 'Comment was not created successfully'
        assert post_response.data is not None, 'HttpResponseError'
        assert post_response.data.get('text') == expected_response.get('text'), 'Wrong text data'
        assert post_response.data.get('id') == expected_response.get('id'), 'Wrong id'
        assert post_response.data.get('goal') == expected_response.get('goal'), 'Wrong goal expected'

    @pytest.mark.django_db
    def test_create_comment_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Comment create test with role reader

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
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        post_response: Any = client.post(
            '/goals/goal_comment/create',
            data={
                "text": "testComment",
                "goal": goal.id
            },
            content_type='application/json',
        )
        expected_response: dict[str, str] = {
            'detail': 'You are allowed only to read, not to create'
        }

        assert post_response.status_code == 403, 'Comment was not created successfully'
        assert post_response.data is not None, 'HttpResponseError'
        assert post_response.data == expected_response

    @pytest.mark.django_db
    def test_retrieve_comment(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Comment retrieve test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 200
            - Response data is not None
            - text field from response == text field from expected_response
            - id field from response == id field from expected_response
            - goal field from response == goal field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        comment: Any = CommentFactory.create(user=user_auth.get('user'), goal=goal)
        response: Any = client.get(
            f'/goals/goal_comment/{comment.id}',
        )
        expected_response: dict[str, list[ReturnDict]] = {
            "id": comment.id,
            "user": [
                UserDetailSerializer(user_auth.get('user')).data
            ],
            "created": goal.created,
            "updated": goal.updated,
            "text": comment.text,
            "goal": comment.goal.id
        }

        assert response.status_code == 200, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data.get('id') == expected_response.get('id'), 'Wrong id expected'
        assert response.data.get('text') == expected_response.get('text'), 'Wrong text expected'
        assert response.data.get('goal') == expected_response.get('goal'), 'Wrong goal expected'

    @pytest.mark.django_db
    def test_retrieve_goal_403(self, client: Any, user_not_auth: dict[str, Any]) -> None:
        """
        Comment retrieve test without authorization

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
        comment: Any = CommentFactory.create(user=user_not_auth, goal=goal)
        response: Any = client.get(
            f'/goals/goal_comment/{comment.id}',
        )
        expected_response: dict[str, str] = {
            "detail": 'Authentication credentials were not provided.'
        }

        assert response.status_code == 403, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_comment_list(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Comment list test

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
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        comment: Any = CommentFactory.create_batch(2, user=user_auth.get('user'), goal=goal)
        expected_response: list[ReturnDict] = [
            CommentSerializer(comment[1]).data,
            CommentSerializer(comment[0]).data,
        ]
        response: Any = client.get('/goals/goal_comment/list')
        assert response.status_code == 200, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_comment_list_403(self, client: Any, user_not_auth: User) -> None:
        """
        Comment list test without authorization

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
        CommentFactory.create_batch(2, user=user_not_auth, goal=goal)
        expected_response: dict[str, str] = {"detail": 'Authentication credentials were not provided.'}
        response: Any = client.get('/goals/goal_comment/list')

        assert response.status_code == 403, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_update_comment(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Comment update test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 200
            - Response data is not None
            - text field from response == text field from expected_response
            - id field from response == id field from expected_response
            - goal field from response == goal field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        comment: Any = CommentFactory.create(user=user_auth.get('user'), goal=goal)
        expected_response: dict[str, str | list[ReturnDict]] = {
            "id": comment.id,
            "user": [UserDetailSerializer(user_auth.get('user')).data],
            "created": comment.goal.created,
            "updated": comment.goal.updated,
            "text": "testComment_edited",
            "goal": comment.goal.id
        }
        put_response: Any = client.put(
            f'/goals/goal_comment/{comment.id}',
            data={
                'text': 'testComment_edited',
            },
            content_type='application/json',
        )

        assert put_response.status_code == 200, 'Goal was not updated successfully'
        assert put_response.data is not None, 'HttpResponseError'
        assert put_response.data.get('text') == expected_response.get('text'), 'Wrong text data'
        assert put_response.data.get('id') == expected_response.get('id'), 'Wrong id'
        assert put_response.data.get('goal') == expected_response.get('goal'), 'Wrong goal expected'

    @pytest.mark.django_db
    def test_update_comment_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Comment update test with role reader

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
        comment: Any = CommentFactory.create(user=user_auth.get('user'), goal=goal)
        expected_response: dict[str, str] = {
            'detail': 'You do not have permission to perform this action.'
        }
        put_response: Any = client.put(
            f'/goals/goal_comment/{comment.id}',
            data={
                'text': 'testComment_edited',
            },
            content_type='application/json',
        )

        assert put_response.status_code == 403, 'Board was edited successfully'
        assert put_response.data is not None, 'HttpResponseError'
        assert put_response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_delete_comment(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Comment delete test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 204
            - Response data is None

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        comment: Any = CommentFactory.create(user=user_auth.get('user'), goal=goal)
        delete_response: Any = client.delete(
            f'/goals/goal_comment/{comment.id}',
        )

        assert delete_response.status_code == 204, 'Goal was not deleted successfully'
        assert delete_response.data is None, 'HttpResponseError'

    @pytest.mark.django_db
    def test_delete_comment_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Comment delete test with role reader

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
        comment: Any = CommentFactory.create(user=user_auth.get('user'), goal=goal)
        expected_response: dict[str, str] = {
            'detail': 'You do not have permission to perform this action.'
        }
        delete_response: Any = client.delete(
            f'/goals/goal_comment/{comment.id}',
        )

        assert delete_response.status_code == 403, 'Category was deleted successfully'
        assert delete_response.data is not None, 'HttpResponseError'
        assert delete_response.data == expected_response, 'Wrong data'
