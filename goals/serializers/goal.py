from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from core.serializers import UserDetailSerializer
from goals.models.board import BoardParticipant
from goals.models.category import GoalCategory
from goals.models.goal import Goal
from goals.serializers.category import CategorySerializer


# ----------------------------------------------------------------
# goal serializers
class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.all()
    )

    def validate_category(self, entity: GoalCategory) -> GoalCategory:
        """Method to validate category entity"""
        current_user = self.context.get('request').user
        board_participant = BoardParticipant.objects.filter(
            board=entity.board,
            user=current_user
        ).first()
        if board_participant.role == BoardParticipant.Role.reader:
            raise PermissionDenied('You are allowed only to read, not to create')
        return entity

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')


class GoalSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    category = CategorySerializer

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields: tuple = ('id', 'created', 'updated', 'user')
