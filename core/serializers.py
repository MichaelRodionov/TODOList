from rest_framework import serializers

from core.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model: User = User
        fields = '__all__'

    def validate(self, data):
        if data.get('password') != data.pop('password_repeat'):
            raise serializers.ValidationError('Password mismatch')
        return data

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(user.password)
        user.save()
        return user
