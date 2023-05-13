from typing import Any

import pytest
from rest_framework.exceptions import ErrorDetail
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import User
from core.serializers import UserDetailSerializer
from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from goals.serializers.category import CategorySerializer
from tests.factories import BoardParticipantFactory, BoardFactory, CategoryFactory, GoalFactory


# ----------------------------------------------------------------
# category tests
class TestCategory:
    @pytest.mark.django_db
    def test_create_category(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category create test

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
        board_participant: Any = BoardParticipantFactory.create(
            board=BoardFactory.create(),
            user=user_auth.get('user')
        )
        expected_response: dict[str, int | bool | str] = {
            'id': 2,
            'title': 'testCategory',
            'board': board_participant.board.id,
            'is_deleted': False,
        }
        post_response: Any = client.post(
            '/goals/goal_category/create',
            data={'title': 'testCategory', 'board': board_participant.board.id},
            content_type='application/json',
        )

        assert post_response.status_code == 201, 'Category was not created successfully'
        assert post_response.data is not None, 'HttpResponseError'
        assert post_response.data.get('title') == expected_response.get('title'), 'Wrong title data'
        assert post_response.data.get('id') == expected_response.get('id'), 'Wrong id'
        assert post_response.data.get('is_deleted') is False, 'Wrong is_deleted status'

    @pytest.mark.django_db
    def test_create_category_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category create test with role reader

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
        expected_response: dict[str, str] = {
            'detail': 'You are allowed only to read, not to create',
        }
        post_response: Any = client.post(
            '/goals/goal_category/create',
            data={'title': 'testCategory', 'board': board_participant.board.id},
            content_type='application/json',
        )

        assert post_response.status_code == 403, 'Category was created successfully'
        assert post_response.data is not None, 'HttpResponseError'
        assert post_response.data == expected_response

    @pytest.mark.django_db
    def test_create_category_400(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category create test when board is deleted

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 400
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
            role=BoardParticipant.Role.writer
        )
        board_participant.board.is_deleted = True
        board_participant.board.save()
        expected_response: dict[str, list[ErrorDetail]] = {
            'board': [ErrorDetail(string="You can't create category in deleted board", code='invalid')]
        }

        post_response: Any = client.post(
            '/goals/goal_category/create',
            data={'title': 'testCategory', 'board': board_participant.board.id},
            content_type='application/json',
        )
        assert post_response.status_code == 400, 'Category was created successfully'
        assert post_response.data is not None, 'HttpResponseError'
        assert post_response.data == expected_response

    @pytest.mark.django_db
    def test_retrieve_category(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category retrieve test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 200
            - Response data is not None
            - title field from response == title field from expected_response
            - id field from response == id field from expected_response
            - is_deleted field from response == is_deleted field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        response: Any = client.get(
            f'/goals/goal_category/{category.id}',
        )
        expected_response: dict[str, list[ReturnDict]] = {
            "id": response.data.get('id'),
            "user": [
                UserDetailSerializer(user_auth.get('user')).data
            ],
            "created": category.created,
            "updated": category.updated,
            "title": category.title,
            "is_deleted": category.is_deleted
        }

        assert response.status_code == 200, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data.get('id') == expected_response.get('id'), 'Wrong id expected'
        assert response.data.get('title') == expected_response.get('title'), 'Wrong title expected'
        assert response.data.get('is_deleted') == expected_response.get('is_deleted'), 'Wrong is_deleted expected'

    @pytest.mark.django_db
    def test_retrieve_category_403(self, client: Any, user_not_auth: User) -> None:
        """
        Category retrieve test without authorization

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
        response: Any = client.get(
            f'/goals/goal_category/{category.id}',
        )
        expected_response: dict[str, str] = {
            "detail": 'Authentication credentials were not provided.'
        }

        assert response.status_code == 403, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_retrieve_category_404(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category retrieve test when category is deleted

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 404
            - Response data is not None
            - response data == data from expected response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(
            board=board_participant.board,
            user=user_auth.get('user'),
            is_deleted=True
        )
        response: Any = client.get(
            f'/goals/goal_category/{category.id}',
        )
        not_expected_response: dict[str, list[ReturnDict]] = {
            "id": response.data.get('id'),
            "user": [
                UserDetailSerializer(user_auth.get('user')).data
            ],
            "created": category.created,
            "updated": category.updated,
            "title": category.title,
            "is_deleted": category.is_deleted
        }

        assert response.status_code == 404, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data != not_expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_category_list(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category list test

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
        categories: Any = CategoryFactory.create_batch(2, board=board_participant.board, user=user_auth.get('user'))
        expected_response: list[ReturnDict] = [
            CategorySerializer(categories[0]).data,
            CategorySerializer(categories[1]).data,
        ]
        response: Any = client.get('/goals/goal_category/list')

        assert response.status_code == 200, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_category_list_403(self, client: Any, user_not_auth: User) -> None:
        """
        Category list test without authorization

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
        CategoryFactory.create_batch(2, board=board_participant.board, user=user_not_auth)
        expected_response: dict[str, str] = {"detail": 'Authentication credentials were not provided.'}
        response: Any = client.get('/goals/goal_category/list')

        assert response.status_code == 403, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_category_list_deleted(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category list test when some categories are deleted

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 200
            - Response data is not None
            - response data is equal expected_response (you should get only two category, because first is deleted)

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        categories: Any = CategoryFactory.create_batch(3, board=board_participant.board, user=user_auth.get('user'))
        categories[0].is_deleted = True
        categories[0].save()
        expected_response: list[ReturnDict] = [
            CategorySerializer(categories[2]).data,
            CategorySerializer(categories[1]).data,
        ]
        response: Any = client.get('/goals/goal_category/list')

        assert response.status_code == 200, 'Status code error'
        assert response.data is not None, 'HttpResponseError'
        assert response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_update_category(self, client: Any, user_auth: dict[str, str]) -> None:
        """
        Category update test

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
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        expected_response: dict[str, str | list[ReturnDict]] = {
            'title': 'testCategory_edited',
            'user': [UserDetailSerializer(user_auth.get('user')).data]
        }
        put_response: Any = client.put(
            f'/goals/goal_category/{category.id}',
            data={
                'title': 'testCategory_edited',
                'board': board_participant.board.id
            },
            content_type='application/json',
        )

        assert put_response.status_code == 200, 'Board was not edited successfully'
        assert put_response.data is not None, 'HttpResponseError'
        assert put_response.data.get('title') == expected_response.get('title'), 'Wrong title data'

    @pytest.mark.django_db
    def test_update_category_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category update test with role reader

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
        expected_response: dict[str, str] = {
            'detail': 'You do not have permission to perform this action.'
        }
        put_response: Any = client.put(
            f'/goals/goal_category/{category.id}',
            data={
                'title': 'testCategory_edited',
                'board': board_participant.board.id
            },
            content_type='application/json',
        )

        assert put_response.status_code == 403, 'Category was edited successfully'
        assert put_response.data is not None, 'HttpResponseError'
        assert put_response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_update_category_404(self, client: Any, user_auth: dict[str, str]) -> None:
        """
        Category update test when category is deleted

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 404
            - Response data is not None
            - Response data is not equal to not expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        category.is_deleted = True
        category.save()
        not_expected_response: dict[str, str | list[ReturnDict]] = {
            'title': 'testCategory_edited',
            'user': [UserDetailSerializer(user_auth.get('user')).data]
        }
        put_response: Any = client.put(
            f'/goals/goal_category/{category.id}',
            data={
                'title': 'testCategory_edited',
                'board': board_participant.board.id
            },
            content_type='application/json',
        )

        assert put_response.status_code == 404, 'Category was edited successfully'
        assert put_response.data is not None, 'HttpResponseError'
        assert put_response.data != not_expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_delete_category(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category delete test

        Params:
            - client: A Django test client instance.
            - user_auth: A fixture that create user instance and login

        Checks:
            - Response status code is 204
            - Response data is None
            - Related instance Goal status field changes to archived

        Returns:
            None

        Raises:
            AssertionError
        """
        board_participant: Any = BoardParticipantFactory.create(user=user_auth.get('user'))
        category: Any = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        delete_response: Any = client.delete(
            f'/goals/goal_category/{category.id}',
        )
        goal.refresh_from_db()

        assert delete_response.status_code == 204, 'Category was not deleted successfully'
        assert delete_response.data is None, 'HttpResponseError'
        assert goal.status == Goal.Status.archived, 'Wrong status expected'

    @pytest.mark.django_db
    def test_delete_category_403(self, client: Any, user_auth: dict[str, Any]) -> None:
        """
        Category delete test with role reader

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
        board_participant = BoardParticipantFactory.create(user=user_auth.get('user'),
                                                           role=BoardParticipant.Role.reader)
        category = CategoryFactory.create(board=board_participant.board, user=user_auth.get('user'))
        goal: Any = GoalFactory.create(category=category, user=user_auth.get('user'))
        expected_response = {
            'detail': 'You do not have permission to perform this action.'
        }
        delete_response = client.delete(
            f'/goals/goal_category/{category.id}',
        )
        goal.refresh_from_db()

        assert delete_response.status_code == 403, 'Category was deleted successfully'
        assert delete_response.data is not None, 'HttpResponseError'
        assert delete_response.data == expected_response, 'Wrong data'
        assert goal.status != Goal.Status.archived, 'Wrong status expected'
