from typing import Type, Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from core.models import User


# ----------------------------------------------------------------
# user serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration serializer

    Attrs:
        - password: current user's password
        - password_repeat: repeat of current password
    """
    password = serializers.CharField(
        required=True
    )
    password_repeat = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs) -> Any:
        """
        Redefined method to validate incoming data

        Params:
            - validated_data: dictionary with validated data of Board entity

        Returns:
            - attrs: dictionary with data

        Raises:
            - ValidationError (in case of password repeat is wrong)

        """
        if attrs.get('password') != attrs.pop('password_repeat'):
            raise serializers.ValidationError('Password mismatch')
        validate_password(attrs.get('password'))
        return attrs

    def create(self, validated_data) -> Any:
        """
        Redefined create method

        Params:
            - validated_data: dictionary with validated data of User entity

        Returns:
            - user: user object
        """
        user = super().create(validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    class Meta:
        model: Type[User] = User
        fields: tuple = ('username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')


class UserDetailSerializer(serializers.ModelSerializer):
    """
    User detail serializer
    """
    class Meta:
        model: Type[User] = User
        fields: tuple = ('id', 'username', 'first_name', 'last_name', 'email')


class UserChangePasswordSerializer(serializers.ModelSerializer):
    """
    User change password serializer

    Attrs:
        - old_password: current user's password
        - new_password: new password
    """
    old_password = serializers.CharField(
        required=True
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )

    def validate(self, attrs):
        """
        Redefined method to validate incoming data

        Params:
            - attrs: dictionary with data of User entity

        Returns:
            - attrs: dictionary with data

        Raises:
            - ValidationError (in case of old_password is wrong or old_password is equal to new_password)
        """
        user = self.context.get('request').user
        old_password, new_password = attrs.get('old_password'), attrs.get('new_password')
        if not user.check_password(old_password):
            raise serializers.ValidationError('Wrong password')

        if new_password is not None and old_password == new_password:
            raise serializers.ValidationError('Similar password')
        return attrs

    def update(self, instance: User, validated_data) -> Any:
        """
        Redefined update method

        Params:
            - instance: User instance
            - validated_data: dictionary with data of User entity

        Returns:
            - User object from parent method
        """
        instance.set_password(validated_data.get('new_password'))
        return super().update(instance, validated_data)

    class Meta:
        model: Type[User] = User
        fields: tuple = ('old_password', 'new_password')
