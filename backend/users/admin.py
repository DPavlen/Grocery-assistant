from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
        'role',
    )
    list_filter = ('email', 'first_name', 'role')



@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настроенная панель (управление подписками)."""
    list_display = (
        'id',
        'user',
        'author'
    )
    search_fields = ('user',)
    list_display = ('id', 'author', 'user')