from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Права для работы Админу."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_admin
        )


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        """Разрешено только чтение для всех."""
        
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Редактирование объекта если user: автор или админ."""

        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_admin
