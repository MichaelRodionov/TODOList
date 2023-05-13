from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.serializers import UserDetailSerializer
from goals.models.board import Board, BoardParticipant
from goals.models.category import GoalCategory


# ----------------------------------------------------------------
# category serializers
class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Category create serializer

    Attrs:
        - user: HiddenField defines current user
        - board: PrimaryKeyRelatedField defines related board
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()
    )

    def validate_board(self, entity: Board) -> Board:
        """
        Redefined method to validate board entity

        Params:
            - entity: Board entity

        Validation:
            - user's role (if role is reader, raise PermissionDenied)
            - board status: raise ValidationError if board is deleted

        Returns:
            - Board entity

        Raises:
            - PermissionDenied
            - ValidationError
        """
        current_user = self.context.get('request').user  # type: ignore
        board_participant = BoardParticipant.objects.filter(
            board=entity,
            user=current_user
        ).first()
        if not board_participant:
            raise PermissionDenied('Board participant not found')
        if board_participant.role == BoardParticipant.Role.reader:
            raise PermissionDenied('You are allowed only to read, not to create')
        if entity.is_deleted:
            raise ValidationError("You can't create category in deleted board")
        return entity

    class Meta:
        model = GoalCategory
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class CategorySerializer(serializers.ModelSerializer):
    """
    Category serializer

    Attrs:
        - user: UserDetailSerializer defines user
        - board: PrimaryKeyRelatedField defines related board
    """
    user = UserDetailSerializer(read_only=True)
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()
    )

    class Meta:
        model = GoalCategory
        fields: str = "__all__"
        read_only_fields: tuple = ("id", "created", "updated", "user", "board")
