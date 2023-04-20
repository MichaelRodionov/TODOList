from django.db import transaction, IntegrityError
from django.db.models import QuerySet
from rest_framework import serializers

from core.models import User
from core.serializers import UserDetailSerializer
from goals import models


# ----------------------------------------------------------------
# board participants serializers
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

    def update(self, entity: models.Board, validated_data: dict) -> models.Board:
        board_owner = validated_data.pop('user')
        elders: QuerySet = entity.participants.exclude(user=board_owner).select_related('user')
        newbies: dict = {user.get('user').id: user for user in validated_data.pop('participants')}
        with transaction.atomic():
            for old in elders:
                if old.user_id not in newbies:
                    old.delete()
                else:
                    if old.role != newbies[old.user_id]['role']:
                        old.role = newbies[old.user_id]['role']
                        old.save()
                    newbies.pop(old.user_id)
            for newbie in newbies.values():
                if newbie.get('user') == board_owner:
                    raise IntegrityError('You cant add yourself as a participant')
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
class CategoryBaseSerializer(serializers.ModelSerializer):
    def validate_board(self, entity: models.Board) -> models.Board:
        """Method to validate category instance"""
        current_user = self.context.get('request').user
        board_participant = models.BoardParticipant.objects.filter(
            board=entity,
            user=current_user
        ).first()
        if board_participant.role == models.BoardParticipant.Role.reader:
            raise serializers.ValidationError('You are allowed only to read, not to edit')
        return entity


class CategoryCreateSerializer(CategoryBaseSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    board = serializers.PrimaryKeyRelatedField(
        queryset=models.Board.objects.all()
    )

    class Meta:
        model = models.GoalCategory
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class CategorySerializer(CategoryBaseSerializer):
    user = UserDetailSerializer(read_only=True)
    board = serializers.PrimaryKeyRelatedField(
        queryset=models.Board.objects.all()
    )

    @staticmethod
    def check_role(entity: models.GoalCategory, current_user) -> bool:
        board_participant = models.BoardParticipant.objects.filter(
            board=entity.board,
            user=current_user
        ).first()
        if board_participant.role == models.BoardParticipant.Role.reader:
            raise serializers.ValidationError('You are allowed only to read, not to delete')
        return True

    class Meta:
        model = models.GoalCategory
        fields: str = "__all__"
        read_only_fields: tuple = ("id", "created", "updated", "user", "board")


# ----------------------------------------------------------------
# goal serializers
class GoalBaseSerializer(serializers.ModelSerializer):
    """Base serializer for goal entity"""
    def validate_category(self, entity: models.GoalCategory) -> models.GoalCategory:
        """Method to validate category entity"""
        current_user = self.context.get('request').user
        board_participant = models.BoardParticipant.objects.filter(
            board=entity.board,
            user=current_user
        ).first()
        if board_participant.role == models.BoardParticipant.Role.reader:
            raise serializers.ValidationError('You are allowed only to read, not to edit')
        return entity

    class Meta:
        model = models.Goal
        fields = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class GoalCreateSerializer(GoalBaseSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=models.GoalCategory.objects.all()
    )


class GoalSerializer(GoalBaseSerializer):
    user = UserDetailSerializer(read_only=True)
    category = CategorySerializer

    @staticmethod
    def check_role(entity: models.Goal, current_user) -> bool:
        board_participant = models.BoardParticipant.objects.filter(
            board=entity.category.board,
            user=current_user
        ).first()
        if board_participant.role == models.BoardParticipant.Role.reader:
            raise serializers.ValidationError(
                'Your role is reader. You are allowed only to read'
            )
        return True


# ----------------------------------------------------------------
# comment serializers
class CommentBaseSerializer(serializers.ModelSerializer):
    """Base serializer for comment entity"""
    def validate_goal(self, entity: models.Goal) -> models.Goal:
        """Method to validate goal entity"""
        current_user = self.context.get('request').user
        board_participant = models.BoardParticipant.objects.filter(
            board=entity.category.board,
            user=current_user
        ).first()
        if board_participant.role == models.BoardParticipant.Role.reader:
            raise serializers.ValidationError(
                'Your role is reader. You are allowed only to read'
            )
        return entity


class CommentCreateSerializer(CommentBaseSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Comment
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class CommentSerializer(CommentBaseSerializer):
    user = UserDetailSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.Comment
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user', 'goal')
