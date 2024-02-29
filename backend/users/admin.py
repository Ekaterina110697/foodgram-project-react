from django.contrib import admin

from users.models import User, Subscribe

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ('email', 'username', 'first_name', 'last_name', 'password')
    list_filter = ('email', 'username')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):

    list_display = ('user', 'author')
