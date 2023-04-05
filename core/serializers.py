from rest_framework import serializers

from core.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model: User = User
        fields = '__all__'

    def validate(self, data):
        print(data)
        if data.get('password') != data.get('password_repeat'):
            raise serializers.ValidationError('Password mismatch')
        data.pop('password_repeat')
        return data

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user
