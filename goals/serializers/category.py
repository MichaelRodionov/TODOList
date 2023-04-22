from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from core.serializers import UserDetailSerializer
from goals.models.board import Board, BoardParticipant
from goals.models.category import GoalCategory


# ----------------------------------------------------------------
# category serializers
class CategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()
    )

    def validate_board(self, entity: Board) -> Board:
        """Method to validate board entity"""
        current_user = self.context.get('request').user
        board_participant = BoardParticipant.objects.filter(
            board=entity,
            user=current_user
        ).first()
        if board_participant.role == BoardParticipant.Role.reader:
            raise PermissionDenied('You are allowed only to read, not to create')
        return entity

    class Meta:
        model = GoalCategory
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class CategorySerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()
    )

    class Meta:
        model = GoalCategory
        fields: str = "__all__"
        read_only_fields: tuple = ("id", "created", "updated", "user", "board")
