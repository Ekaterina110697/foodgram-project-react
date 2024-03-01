from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag

User = get_user_model()


class IngredientFilter(SearchFilter):
    """Фильтр для полученяи ингридиентов."""
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """Фильтр для полученяи рецептов."""
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(method='get_check_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_check_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_check_favorited(self, queryset, name, value):
        """Проверка наличия рецепта в избранном."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_check_shopping_cart(self, queryset, name, value):
        """Проверка наличия рецепта в списке покупок."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset
