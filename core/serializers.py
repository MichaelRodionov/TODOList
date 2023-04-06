from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from core.models import User


# ----------------------------------------------------------------
# user serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)
    password_repeat = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs.get('password') != attrs.pop('password_repeat'):
            raise serializers.ValidationError('Password mismatch')
        validate_password(attrs.get('password'))
        return attrs

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    class Meta:
        model: User = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')
