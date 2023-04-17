from django.db import transaction
from django.db.models import QuerySet
from rest_framework import serializers

from core.models import User
from core.serializers import UserDetailSerializer
from goals import models


# ----------------------------------------------------------------
# board serializers
class BoardCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        user = validated_data.pop("user")
        board = models.Board.objects.create(**validated_data)
        models.BoardParticipant.objects.create(
            user=user,
            board=board,
            role=models.BoardParticipant.Role.owner
        )
        return board

    class Meta:
        model = models.Board
        read_only_fields = ("id", "created", "updated")
        fields = "__all__"


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Board
        fields = "__all__"


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        required=True,
        choices=models.BoardParticipant.Role.choices
    )
    user = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.all()
    )

    class Meta:
        model = models.BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


class BoardSerializer(serializers.ModelSerializer):
    participants = BoardParticipantSerializer(
        many=True
    )
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")

    def update(self, entity: models.Board, validated_data):
        board_owner = validated_data.pop('user')
        elders: QuerySet = entity.participants.exclude(user=board_owner)
        newbies: dict = {user.get('user').id: user for user in validated_data.pop('participants')}
        with transaction.atomic():
            for older in elders:
                if older.user_id not in newbies:
                    older.delete()
                else:
                    if older.role != newbies[older.user_id]['role']:
                        older.role = newbies[older.user_id]['role']
                        older.save()
                    newbies.pop(older.user_id)
            for newbie in newbies.values():
                models.BoardParticipant.objects.create(
                    board=entity,
                    user=newbie.get('user'),
                    role=newbie.get('role')
                )
        entity.title = validated_data.get('title')
        entity.save()
        return entity


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
    goal = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.Comment
        fields = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user', 'goal')
