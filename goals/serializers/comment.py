from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.serializers import UserDetailSerializer
from goals.models.board import BoardParticipant
from goals.models.comment import Comment
from goals.models.goal import Goal


# ----------------------------------------------------------------
# comment serializers
class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Comment create serializer

    Attrs:
        - user: HiddenField defines current user'
    """
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_goal(self, entity: Goal) -> Goal:
        """
        Redefined method to validate goal entity

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
            board=entity.category.board,
            user=current_user
        ).first()
        if not board_participant:
            raise PermissionDenied('Board participant not found')
        if board_participant.role == BoardParticipant.Role.reader:
            raise PermissionDenied('You are allowed only to read, not to create')
        if entity.status == Goal.Status.archived:
            raise ValidationError("You can't create comment in archived goal")
        return entity

    class Meta:
        model = Comment
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer

    Attrs:
        - user: UserDetailSerializer defines user
        - goal: PrimaryKeyRelatedField defines related goal
    """
    user = UserDetailSerializer(read_only=True)
    goal: serializers.PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user', 'goal')
