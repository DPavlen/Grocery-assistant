from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Действие может выполнять строго только админ."""

    def has_permission(self, request,view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
        )


class IsAuthorOrAdminOrIsAuthReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        """Только автор или админ могут менять или удалять свой контент."""

        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    # def has_object_permission(self, request, view, obj):
    #     """Редактирование объекта если user: автор или админ."""

    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #     return obj.author == request.user or request.user.is_admin
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )


class IsAuthorPermission(permissions.BasePermission):
    """Только автор может добавлять/удалять в списки:
    избранных рецептов(favorite), списки покупок(shopping_cart), 
    А также подписываться/отписываться от пользователей."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
