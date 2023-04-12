from rest_framework import serializers

from core.serializers import UserDetailSerializer
from goals import models


# ----------------------------------------------------------------
# category serializers
class CategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.GoalCategory
        fields = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class CategorySerializer(CategoryCreateSerializer):
    user = UserDetailSerializer(read_only=True)


# ----------------------------------------------------------------
# goal serializers
class GoalDefaultSerializer(serializers.ModelSerializer):
    """Default serializer with Meta"""
    class Meta:
        model = models.Goal
        fields = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class GoalCreateSerializer(GoalDefaultSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=models.GoalCategory.objects.all()
    )

    def validate_category(self, instance: models.GoalCategory) -> models.GoalCategory:
        """Method to validate category instance"""
        if instance.is_deleted:
            raise serializers.ValidationError('You can not add goal in deleted category')
        if instance.user != self.context.get('request').user:
            raise serializers.ValidationError('Not your own category')
        return instance


class GoalSerializer(GoalDefaultSerializer):
    user = UserDetailSerializer(read_only=True)
    category = CategorySerializer


# ----------------------------------------------------------------
# comment serializers
class CommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_goal(self, instance: models.Goal) -> models.Goal:
        """Method to validate goal instance"""
        if instance.status == models.Goal.Status.archived:
            raise serializers.ValidationError('You can not add comment in archived goal')
        if instance.user != self.context.get('request').user:
            raise serializers.ValidationError('Not your own goal')
        return instance

    class Meta:
        model = models.Comment
        fields = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class CommentSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    goal = GoalSerializer

    class Meta:
        model = models.Comment
        fields = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user', 'goal')
