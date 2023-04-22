from rest_framework import permissions

from goals.models.board import BoardParticipant
from goals.models.category import GoalCategory
from goals.models.comment import Comment
from goals.models.goal import Goal


# ----------------------------------------------------------------
# boar permissions
class BoardPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """Method to check board permissions"""
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj
            ).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner
        ).exists()


# ----------------------------------------------------------------
# category permissions
class CategoryPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        """Method to check category permissions"""
        if request.method in permissions.SAFE_METHODS:
            return GoalCategory.objects.select_related('board').filter(
                board__participants__user=request.user,
                board=obj.board
            ).exists()
        else:
            return GoalCategory.objects.select_related('board').filter(
                board__participants__user=request.user,
                board=obj.board,
                board__participants__role__in=[
                    BoardParticipant.Role.owner,
                    BoardParticipant.Role.writer
                ]
            ).exists()


# ----------------------------------------------------------------
# goal permissions
class GoalPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        """Method to check goal permissions"""
        if request.method in permissions.SAFE_METHODS:
            return Goal.objects.select_related('category').filter(
                category__board__participants__user=request.user,
                category__board=obj.category.board
            ).exists()
        else:
            return Goal.objects.select_related('category').filter(
                category__board__participants__user=request.user,
                category__board=obj.category.board,
                category__board__participants__role__in=[
                    BoardParticipant.Role.owner,
                    BoardParticipant.Role.writer
                ]
            ).exists()


# ----------------------------------------------------------------
# comments permissions
class CommentPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        """Method to check comment permissions"""
        if request.method in permissions.SAFE_METHODS:
            return Comment.objects.select_related('goal').filter(
                goal__category__board__participants__user=request.user,
                goal__category__board=obj.goal.category.board
            ).exists()
        else:
            return Comment.objects.select_related('goal').filter(
                goal__category__board__participants__user=request.user,
                goal__category__board=obj.goal.category.board,
                goal__category__board__participants__role__in=[
                    BoardParticipant.Role.owner,
                    BoardParticipant.Role.writer
                ]
            ).exists()
