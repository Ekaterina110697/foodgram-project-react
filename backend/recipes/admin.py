from django.contrib import admin

from .models import (Ingredient, Recipe, RecipeIngredient, Tag, UserFavorites,
                     UserShoppingCart)

admin.site.empty_value_display = 'Не задано'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображает ингредиенты в панели администратора."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображает теги в панели администратора."""
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображает рецепты в панели администратора."""
    list_display = (
        'author', 'name', 'text',
        'cooking_time', 'pub_date',)
    search_fields = ('author', 'name', 'tags')
    list_filter = ('pub_date', 'tags',)
    inlines = (RecipeIngredientInline,)


@admin.register(UserFavorites)
class UserFavoritesAdmin(admin.ModelAdmin):
    """Отображает подписки на авторов в панели администратора."""
    list_display = ('user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(UserShoppingCart)
class UserShoppingCartAdmin(admin.ModelAdmin):
    """Отображает корзину в панели администратора."""
    list_display = ('recipe',)
    search_fields = ('user',)
    list_filter = ('user',)
