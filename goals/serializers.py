from rest_framework import serializers

from core.serializers import UserDetailSerializer
from goals import models


# ----------------------------------------------------------------
# category serializers
class CategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.GoalCategory
        read_only_fields = ('id', 'created', 'updated', 'user')
        fields = '__all__'


class CategorySerializer(CategoryCreateSerializer):
    user = UserDetailSerializer(read_only=True)


# ----------------------------------------------------------------
# goal serializers
class GoalDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'author', 'category')


class GoalCreateSerializer(GoalDefaultSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=models.GoalCategory.objects.all()
    )

    def validate_category(self, instance: models.GoalCategory):
        if instance.is_deleted:
            raise serializers.ValidationError('You can not add goal in deleted category')
        if instance.user != self.context.get('request').user:
            raise serializers.ValidationError('Not your own category')
        return instance


class GoalSerializer(GoalDefaultSerializer):
    author = UserDetailSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
