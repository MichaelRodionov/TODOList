from typing import Any

import pytest
from rest_framework.exceptions import ErrorDetail

from core.models import User
from tests.factories import UserFactory


# ----------------------------------------------------------------
# user tests
class TestUser:
    @pytest.mark.django_db
    def test_registrate_user(self, client: Any) -> None:
        """
        User registration success test

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 201
            - Response data is not None
            - user from database exists
            - users username is equal to username of user from user factory

        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory, reg_response = self.build_and_reg(client)
        user_db: User = User.objects.get(username=user_factory.username)

        assert reg_response.data is not None, 'Wrong response'
        assert reg_response.status_code == 201, 'Wrong status code'
        assert user_db is not None, 'User not found'
        assert user_db.username == user_factory.username, 'Wrong username expected'

    @pytest.mark.django_db
    def test_registrate_user_400(self, client: Any) -> None:
        """
        User registration test with 400 response because of wrong password repeat field

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 400
            - Response data is not None
            - Response data == expected data
            - User is not exists in database

        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory: Any = UserFactory.build()
        post_response: Any = client.post(
            '/core/signup',
            {
                'username': user_factory.username,
                'password': user_factory.password,
                'password_repeat': '123Qwert!@#'
            }
        )
        expected_response: dict[str, list[ErrorDetail]] = {
            'non_field_errors':
                [ErrorDetail(string='Password mismatch', code='invalid')]
        }

        assert post_response.data is not None, 'Wrong response'
        assert post_response.status_code == 400, 'Wrong status code'
        assert post_response.data == expected_response
        assert User.objects.filter(username=user_factory.username).exists() is False, 'User found'

    @pytest.mark.django_db
    def test_login_user(self, client: Any) -> None:
        """
        User authentication success test

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 400
            - Response data is not None
            - Response data == expected data

        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory, reg_response = self.build_and_reg(client)

        response_auth: Any = self.user_login(client, data={
            'username': user_factory.username,
            'password': user_factory.password,
        })
        expected_response: str = 'Successful login'

        assert response_auth.status_code == 201, 'Wrong status code'
        assert response_auth.data is not None, 'Wrong response'
        assert response_auth.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_login_user_403(self, client: Any) -> None:
        """
        User login test with 403 response because of wrong password field

        Params:
            - client: A Django test client instance.

        Checks:
            - Response auth try 1 status code is 403
            - Response auth try 1 data is not None
            - Response auth try 1 data == expected data
            - Response auth try 2 status code is 403
            - Response auth try 2 data is not None
            - Response auth try 2 data == expected data

        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory, reg_response = self.build_and_reg(client)
        response_auth_1: Any = self.user_login(client, data={
            'username': user_factory.username,
            'password': '123Qwert!@#',
        })
        response_auth_2: Any = self.user_login(client, data={
            'username': 'random_username',
            'password': user_factory.password
        })
        expected_response: dict[str, ErrorDetail] = {
            'detail': ErrorDetail(string='Invalid username or password', code='authentication_failed')
        }

        assert response_auth_1.status_code == 403, 'Wrong status code'
        assert response_auth_1.data is not None, 'Wrong response'
        assert response_auth_1.data == expected_response, 'Wrong data expected'
        assert response_auth_2.status_code == 403, 'Wrong status code'
        assert response_auth_2.data is not None, 'Wrong response'
        assert response_auth_2.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_get_user_data(self, client: Any) -> None:
        """
        Get user's profile test

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 200
            - Response data is not None
            - id field from response == id field from expected_response
            - username field from response == username field from expected_response
            - first_name field from response == first_name field from expected_response
            - last_name field from response == last_name field from expected_response
            - email field from response == email field from expected_response

        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory, reg_response = self.build_and_reg(client)
        self.user_login(client, data={
            'username': user_factory.username,
            'password': user_factory.password
        })
        user_db: User = User.objects.get(username=user_factory.username)
        profile_response: Any = client.get(
            '/core/profile',
        )
        expected_response: dict[str, str | int] = {
            'id': user_db.pk,
            'username': user_db.username,
            'first_name': user_db.first_name,
            'last_name': user_db.last_name,
            'email': user_db.email
        }

        assert profile_response.status_code == 200, 'Wrong status code'
        assert profile_response.data is not None, 'Wrong response data'
        assert profile_response.data.get('id') == expected_response.get('id'), 'Wrong id'
        assert profile_response.data.get('username') == expected_response.get('username'), 'Wrong username'
        assert profile_response.data.get('first_name') == expected_response.get('first_name'), 'Wrong first_name'
        assert profile_response.data.get('last_name') == expected_response.get('last_name'), 'Wrong last_name'
        assert profile_response.data.get('email') == expected_response.get('email'), 'Wrong email'

    @pytest.mark.django_db
    def test_get_user_data_403(self, client: Any) -> None:
        """
        Get user's profile test with 403 response because of no authentication

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 403
            - Response data is not None
            - Response data is equal expected data

        Returns:
            None

        Raises:
            AssertionError
        """
        self.build_and_reg(client)
        profile_response = client.get(
            '/core/profile',
        )
        expected_response: dict[str, str] = {
            'detail': 'Authentication credentials were not provided.'
        }

        assert profile_response.status_code == 403, 'Wrong status code'
        assert profile_response.data is not None, 'Wrong response data'
        assert profile_response.data == expected_response, 'Wrong data'

    @pytest.mark.django_db
    def test_update_user_data(self, client: Any) -> None:
        """
        Update user's profile's fields test

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 200
            - Response data is not None
            - Response data is equal expected data

        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory, reg_response = self.build_and_reg(client)
        user_db: User = User.objects.get(username=user_factory.username)
        self.user_login(client, data={
            'username': user_factory.username,
            'password': user_factory.password
        })
        put_response: Any = client.patch(
            '/core/profile',
            data={
                'email': 'test@mail.ru',
                'first_name': 'testFirst',
                'last_name': 'testLast'
            },
            content_type='application/json',
        )
        user_db.refresh_from_db()
        expected_response: dict[str, str | int] = {
            'id': user_db.pk,
            'username': user_db.username,
            'first_name': 'testFirst',
            'last_name': 'testLast',
            'email': 'test@mail.ru',
        }

        assert put_response.status_code == 200, 'wrong'
        assert put_response.data is not None, 'Wrong response'
        assert put_response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_update_user_data_403(self, client: Any) -> None:
        """
        Update user's profile's fields test with 403 response because of no authentication

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 403
            - Response data is not None
            - Response data is equal expected data

        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory, reg_response = self.build_and_reg(client)
        user_db: User = User.objects.get(username=user_factory.username)
        put_response: Any = client.patch(
            '/core/profile',
            data={
                'email': 'test@mail.ru',
                'first_name': 'testFirst',
                'last_name': 'testLast'
            },
            content_type='application/json',
        )
        user_db.refresh_from_db()
        expected_response: dict[str, ErrorDetail] = {
            'detail': ErrorDetail(
                string='Authentication credentials were not provided.',
                code='not_authenticated')
        }

        assert put_response.status_code == 403, 'wrong'
        assert put_response.data is not None, 'Wrong response'
        assert put_response.data == expected_response, 'Wrong data expected'

    @pytest.mark.django_db
    def test_update_user_password(self, client: Any) -> None:
        """
        Update user's password test

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 200
            - Response data is not None
            - Response data is equal expected data
            - password_check returns True if password is correct
            - login try 1 is not successful, because try login with old password
            - login try 2 is successful, because try login with new password


        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory, reg_response = self.build_and_reg(client)
        user_db: User = User.objects.get(username=user_factory.username)
        self.user_login(client, data={
            'username': user_factory.username,
            'password': user_factory.password
        })
        post_response: Any = client.put(
            '/core/update_password',
            data={
                'old_password': user_factory.password,
                'new_password': 'newP@ssword12#',
            },
            content_type='application/json',
        )
        password_check: bool = user_db.check_password(user_factory.password)
        user_db.refresh_from_db()
        expected_response: dict[str, str] = {
            'old_password': user_factory.password,
            'new_password': 'newP@ssword12#',
        }
        try_login_1: Any = self.user_login(client, data={
            'username': user_factory.username,
            'password': user_factory.password
        })
        try_login_2: Any = self.user_login(client, data={
            'username': user_factory.username,
            'password': 'newP@ssword12#'
        })
        expected_response_login: str = 'Successful login'

        assert password_check is True, 'Wrong password'
        assert post_response.status_code == 200, 'wrong'
        assert post_response.data is not None, 'Wrong response'
        assert post_response.data == expected_response, 'Wrong data expected'
        assert try_login_1.data != expected_response_login, 'Wrong data expected'
        assert try_login_2.data == expected_response_login, 'Wrong data expected'

    @pytest.mark.django_db
    def test_update_user_password_400_wrong_old_password(self, client: Any) -> None:
        """
        Update user's password test with 400 response because of wrong old password

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 400
            - Response data is not None
            - Response data is equal expected data
            - password_check returns True if old password still in database

        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory, reg_response = self.build_and_reg(client)
        user_db: User = User.objects.get(username=user_factory.username)
        self.user_login(client, data={
            'username': user_factory.username,
            'password': user_factory.password
        })
        post_response: Any = client.put(
            '/core/update_password',
            data={
                'old_password': 'wr0ngP@ssword12#',
                'new_password': 'newP@ssword12#',
            },
            content_type='application/json',
        )
        user_db.refresh_from_db()
        password_check: bool = user_db.check_password(user_factory.password)
        expected_response: dict[str, list[ErrorDetail]] = {
            'non_field_errors': [ErrorDetail(string='Wrong password', code='invalid')]
        }

        assert post_response.status_code == 400, 'wrong'
        assert post_response.data is not None, 'Wrong response'
        assert post_response.data == expected_response, 'Wrong data expected'
        assert password_check is True, 'Password changed'

    @pytest.mark.django_db
    def test_update_user_password_400_similar_password(self, client: Any) -> None:
        """
        Update user's password test with 400 response because of new password is similar to old password

        Params:
            - client: A Django test client instance.

        Checks:
            - Response status code is 400
            - Response data is not None
            - Response data is equal expected data
            - password_check returns True if old password still in database

        Returns:
            None

        Raises:
            AssertionError
        """
        user_factory, reg_response = self.build_and_reg(client)
        user_db: User = User.objects.get(username=user_factory.username)
        self.user_login(client, data={
            'username': user_factory.username,
            'password': user_factory.password
        })
        post_response: Any = client.put(
            '/core/update_password',
            data={
                'old_password': user_factory.password,
                'new_password': user_factory.password,
            },
            content_type='application/json',
        )
        user_db.refresh_from_db()
        password_check: bool = user_db.check_password(user_factory.password)
        expected_response: dict[str, list[ErrorDetail]] = {
            'non_field_errors': [ErrorDetail(string='Similar password', code='invalid')]
        }

        assert post_response.status_code == 400, 'wrong'
        assert post_response.data is not None, 'Wrong response'
        assert post_response.data == expected_response, 'Wrong data expected'
        assert password_check is True, 'Password changed'

    @pytest.mark.django_db
    def test_user_logout(self, client: Any) -> None:
        """
         User's logout test

         Params:
             - client: A Django test client instance.

         Checks:
             - Response status code is 204
             - Response data is not None
             - Response data is equal to expected data
             - response 2 (try to get users profile) status code is 403 because user is not authenticated
             - response 2 data is equal to expected data 2

         Returns:
             None

         Raises:
             AssertionError
         """
        user_factory, reg_response = self.build_and_reg(client)
        self.user_login(client, data={
            'username': user_factory.username,
            'password': user_factory.password
        })
        delete_response: Any = client.delete(
            '/core/profile',
            content_type='application/json',
        )
        expected_response_1: str = 'Successful logout'
        profile_response: Any = client.get(
            '/core/profile',
        )
        expected_response_2: dict[str, str] = {
            'detail': 'Authentication credentials were not provided.'
        }

        assert delete_response.status_code == 204, 'Wrong status code'
        assert delete_response.data is not None, 'Wrong response'
        assert delete_response.data == expected_response_1, 'Wrong data expected'
        assert profile_response.status_code == 403, 'Wrong status code'
        assert profile_response.data is not None, 'Wrong response'
        assert profile_response.data == expected_response_2, 'Wrong data expected'

    @staticmethod
    @pytest.mark.django_db
    def build_and_reg(client) -> tuple[Any, Any]:
        """
        Simple function to build user by user factory and add him to database

        Params:
            - client: A Django test client instance.

        Returns:
            Tuple with user entity and registration response
        """
        user_factory = UserFactory.build()
        reg_response = client.post(
            '/core/signup',
            {
                'username': user_factory.username,
                'password': user_factory.password,
                'password_repeat': user_factory.password
            }
        )
        return user_factory, reg_response

    @staticmethod
    @pytest.mark.django_db
    def user_login(client: Any, data) -> Any:
        """
        Simple function that authenticate user by post request with user's data

        Params:
            - client: A Django test client instance.
            - data: dict with username and password params

        Returns:
            Tuple with user entity and registration response
        """
        response_auth: Any = client.post(
            '/core/login',
            {
                'username': data.get('username'),
                'password': data.get('password'),
            },
            format='json'
        )
        return response_auth
