from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.serializers import UserDetailSerializer
from goals.models.board import BoardParticipant
from goals.models.category import GoalCategory
from goals.models.goal import Goal
from goals.serializers.category import CategorySerializer


# ----------------------------------------------------------------
# goal serializers
class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Category create serializer

    Attrs:
        - user: HiddenField defines current user
        - category: PrimaryKeyRelatedField defines related category
    """
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.all()
    )

    def validate_category(self, entity: GoalCategory) -> GoalCategory:
        """
        Redefined method to validate category entity

        Params:
            - entity: Goal entity

        Validation:
            - user's role (if role is reader, raise PermissionDenied)

        Returns:
            - Goal entity

        Raises:
            - PermissionDenied
        """
        current_user = self.context.get('request').user  # type: ignore
        board_participant = BoardParticipant.objects.filter(
            board=entity.board,
            user=current_user
        ).first()
        if not board_participant:
            raise PermissionDenied('Board participant not found')
        if board_participant.role == BoardParticipant.Role.reader:
            raise PermissionDenied('You are allowed only to read, not to create')
        if entity.is_deleted:
            raise ValidationError("You can't create goal in deleted category")
        return entity

    class Meta:
        model = Goal
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class GoalSerializer(serializers.ModelSerializer):
    """
    Goal serializer

    Attrs:
        - user: UserDetailSerializer defines user
        - category: CategorySerializer defines related category
    """
    user = UserDetailSerializer(read_only=True)
    category = CategorySerializer

    class Meta:
        model = Goal
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')
