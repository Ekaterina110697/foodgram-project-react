from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.settings import (RECIPE_EXISTS, RECIPE_NO_IN_FAVORITE,
                               RECIPE_NO_IN_SHOPPING_CART, RECIPE_NOT_FOUND)
from recipes.models import (Ingredient, Recipe, RecipeIngredient, Tag,
                            UserFavorites, UserShoppingCart)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, IngredientsSerializer,
                          ReadRecipeSerializer, TagSerializer,
                          UserFavoritesSerializer, UserShoppingCartSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта.
       Просмотр, создание, редактирование."""
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = self.request.user
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            user = request.user
            recipe_id = self.kwargs.get('pk')
            recipe = Recipe.objects.filter(id=recipe_id).first()
            if not recipe:
                return Response(RECIPE_NOT_FOUND,
                                status=status.HTTP_400_BAD_REQUEST)
            if UserFavorites.objects.filter(user=user, recipe=recipe).exists():
                return Response(RECIPE_EXISTS,
                                status=status.HTTP_400_BAD_REQUEST)
            UserFavorites.objects.create(user=user, recipe=recipe)
            serializer = UserFavoritesSerializer(recipe,
                                                 context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            user_favorites = UserFavorites.objects.filter(user=user,
                                                          recipe=recipe)
            if not user_favorites:
                return Response(RECIPE_NO_IN_FAVORITE,
                                status=status.HTTP_400_BAD_REQUEST)
            user_favorites.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            user = request.user
            recipe_id = self.kwargs.get('pk')
            recipe = Recipe.objects.filter(id=recipe_id).first()
            if not recipe:
                return Response(RECIPE_NOT_FOUND,
                                status=status.HTTP_400_BAD_REQUEST)
            if UserShoppingCart.objects.filter(user=user,
                                               recipe=recipe).exists():
                return Response(RECIPE_EXISTS,
                                status=status.HTTP_400_BAD_REQUEST)
            UserShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = UserShoppingCartSerializer(
                recipe, context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            user_shopping_cart = UserShoppingCart.objects.filter(user=user,
                                                                 recipe=recipe)
            if not user_shopping_cart:
                return Response(RECIPE_NO_IN_SHOPPING_CART,
                                status=status.HTTP_400_BAD_REQUEST)
            user_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['GET'],
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_cart = []
        for ingredient in ingredients:
            shopping_cart.append(
                f'{ingredient["ingredient__name"]}'
                f'({ingredient["ingredient__measurement_unit"]})'
                f'- {ingredient["amount"]}\n'
                )
        filename = "shopping_cart.txt"
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
