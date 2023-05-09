from typing import Any

import pytest
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import User
from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from goals.serializers.board import BoardParticipantSerializer, BoardListSerializer
from tests.factories import BoardParticipantFactory, CategoryFactory, GoalFactory


# ----------------------------------------------------------------
# board tests
class TestBoard:
    @pytest.mark.django_db
    def test_create_board(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Board create test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 201
            - Response data is not None
            - title field from response == title field from expected_response
            - id field from response == id field from expected_response
            - is_deleted field from response == is_deleted field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        expected_response: dict[str, str | int] = {
            'id': 1,
            'title': 'testBoard',
        }

        post_response: Any = client.post(
            '/goals/board/create',
            data={'title': 'testBoard'},
            content_type='application/json',
        )

        assert post_response.status_code == 201, 'Board was not created successfully'
        assert post_response.data is not None, 'HttpResponseError'
        assert post_response.data.get('title') == expected_response.get('title'), 'Wrong title data'
        assert post_response.data.get('id') == expected_response.get('id'), 'Wrong id'
        assert post_response.data.get('is_deleted') is False, 'Wrong is_deleted status'

    @pytest.mark.django_db
    def test_create_board_403(self, client: Any, user_not_auth: User) -> None:
        """
        Board create test without authorization

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
        expected_response: dict[str, str] = {
            'detail': 'Authentication credentials were not provided.'
        }

        post_response: Any = client.post(
            '/goals/board/create',
            data={'title': 'testBoard'},
            content_type='application/json',

        )

        assert post_response.status_code == 403, 'Status code error'
        assert post_response.data is not None, 'HttpResponseError'
        assert post_response.data == expected_response

    @pytest.mark.django_db
    def test_retrieve_board(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Board retrieve test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 200
            - Response data is not None
            - title field from response == title field from expected_response
            - id field from response == id field from expected_response
            - is_deleted field from response == is_deleted field from expected_response
            - participants field from response == participants field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))

        response: Any = client.get(
            f'/goals/board/{board_participant.board.id}',
        )
        expected_response: dict[str, list[ReturnDict]] = {
            "id": response.data.get('id'),
            "participants": [
                BoardParticipantSerializer(board_participant).data
            ],
            "created": board_participant.board.created,
            "updated": board_participant.board.updated,
            "title": board_participant.board.title,
            "is_deleted": board_participant.board.is_deleted
        }

        assert response.status_code == 200, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data.get('id') == expected_response.get('id'), 'Wrong id expected'
        assert response.data.get('title') == expected_response.get('title'), 'Wrong title expected'
        assert response.data.get('is_deleted') == expected_response.get('is_deleted'), 'Wrong is_deleted expected'
        assert response.data.get('participants') == expected_response.get('participants'), 'Wrong participants expected'

    @pytest.mark.django_db
    def test_retrieve_board_403(self, client: Any, user_not_auth: User) -> None:
        """
        Board retrieve test without authorization

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

        response: Any = client.get(
            f'/goals/board/{board_participant.board.id}',
        )
        expected_response: dict[str, str] = {
            "detail": 'Authentication credentials were not provided.'

        }

        assert response.status_code == 403, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_board_list(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Board list test

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
        board_participants: Any = BoardParticipantFactory.create_batch(2, user=user_auth.get('user'))
        expected_response: list[ReturnDict] = [
            BoardListSerializer(board_participants[0].board).data,
            BoardListSerializer(board_participants[1].board).data,
        ]
        response = client.get('/goals/board/list')

        assert response.status_code == 200, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_board_list_403(self, client: Any, user_not_auth: User) -> None:
        """
        Board list test without authorization

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
        BoardParticipantFactory.create_batch(2, user=user_not_auth)
        expected_response: dict[str, str] = {"detail": 'Authentication credentials were not provided.'}
        response: Any = client.get('/goals/board/list')

        assert response.status_code == 403, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_update_board(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Board update test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 200
            - Response data is not None
            - title field from response == title field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        expected_response: dict[str, str | list] = {
            'title': 'testBoard_edited',
            'participants': []
        }
        put_response: Any = client.put(
            f'/goals/board/{board_participant.board.id}',
            data={
                'title': 'testBoard_edited',
                'participants': []
            },
            content_type='application/json',
        )

        assert put_response.status_code == 200, 'Board was not edited successfully'
        assert put_response.data is not None, 'HttpResponseError'
        assert put_response.data.get('title') == expected_response.get('title'), 'Wrong title data'

    @pytest.mark.django_db
    def test_update_board_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Board update test with role reader

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
        expected_response: dict[str, str] = {
            'detail': 'You do not have permission to perform this action.'
        }
        put_response: Any = client.put(
            f'/goals/board/{board_participant.board.id}',
            data={
                'title': 'testBoard_edited',
                'participants': []
            },
            content_type='application/json',
        )

        assert put_response.status_code == 403, 'Board was edited successfully'
        assert put_response.data is not None, 'HttpResponseError'
        assert put_response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_delete_board(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Board delete test

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
        delete_response: Any = client.delete(
            f'/goals/board/{board_participant.board.id}',
        )

        assert delete_response.status_code == 204, 'Board was not deleted successfully'
        assert delete_response.data is None, 'HttpResponseError'

    @pytest.mark.django_db
    def test_delete_board_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Board delete test with role reader

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
        expected_response: dict[str, str] = {
            'detail': 'You do not have permission to perform this action.'
        }
        delete_response: Any = client.delete(
            f'/goals/board/{board_participant.board.id}',
        )

        assert delete_response.status_code == 403, 'Board was deleted successfully'
        assert delete_response.data is not None, 'HttpResponseError'
        assert delete_response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_entities_change_status(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Board delete test and related instances status check

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 204
            - Category is_deleted status changes to True
            - Goal status changes to archived

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        delete_response: Any = client.delete(
            f'/goals/board/{board_participant.board.id}',
        )
        category.refresh_from_db()
        goal.refresh_from_db()

        assert delete_response.status_code == 204, 'Wrong'
        assert category.is_deleted is True, 'Category was not deleted successfully'
        assert goal.status == Goal.Status.archived, 'Wrong status expected'
