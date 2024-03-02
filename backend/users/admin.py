from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as Admin

from users.models import Subscribe

admin.site.empty_value_display = 'Не задано'

User = get_user_model()


@admin.register(User)
class UserAdmin(Admin):

    list_display = ('email', 'username', 'first_name', 'last_name', 'password')
    list_filter = ('email', 'username')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):

    list_display = ('user', 'author')
