from django.contrib import admin

from .models import User, Subscriptions


class BaseAdminSettings(admin.ModelAdmin):
    """Базовая настроенная админ панели."""
    empty_value_display = '-пусто-'
    list_filter = ('email', 'username')


class UsersAdmin(BaseAdminSettings):
    """Настроенная панель админки (управление пользователями)."""
    list_display = (
        'id',
        'role',
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_display_links = ('id', 'username')
    search_fields = ('username', 'role')


admin.site.register(User, UsersAdmin)


@admin.register(Subscriptions)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настроенная панель (управление подписками)."""
    list_display = (
        'id',
        'user',
        'author'
    )
    search_fields = ('user',)
    list_display = ('id', 'author', 'user')
