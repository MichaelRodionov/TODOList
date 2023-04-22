from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from core.serializers import UserDetailSerializer
from goals.models.board import BoardParticipant
from goals.models.comment import Comment
from goals.models.goal import Goal


# ----------------------------------------------------------------
# comment serializers
class CommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_goal(self, entity: Goal) -> Goal:
        """Method to validate goal entity"""
        current_user = self.context.get('request').user
        board_participant = BoardParticipant.objects.filter(
            board=entity.category.board,
            user=current_user
        ).first()
        if board_participant.role == BoardParticipant.Role.reader:
            raise PermissionDenied('You are allowed only to read, not to create')
        return entity

    class Meta:
        model = Comment
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class CommentSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields: str = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user', 'goal')
