from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.constants import SUBSCRIBE_NO_EXISTS
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer, IngredientsSerializer,
                             ReadRecipeSerializer, SubscribesListSerializer,
                             TagSerializer, UserFavoritesSerializer,
                             UserProfileSerializer, UserShoppingCartSerializer,
                             AddRemoveSubcribeSerializer)
from recipes.models import (Ingredient, Recipe, RecipeIngredient, Tag,
                            UserFavorites, UserShoppingCart)
from users.models import Subscribe

User = get_user_model()


class UserSubscribeViewSet(UserViewSet):
    """Вьюсет пользователя.Управление подписками"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (AllowAny, )

    def get_permissions(self):
        """Распределение прав на действия."""
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(publisher__user=user)
        paginate_page = self.paginate_queryset(subscriptions)
        serializer = SubscribesListSerializer(
            paginate_page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        if request.method == 'POST':
            data = {
                'user': request.user.id,
                'author': id
            }
            serializer = AddRemoveSubcribeSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author = get_object_or_404(User, id=id)
            response = SubscribesListSerializer(
                author, context={'request': request}
            )
            return Response(
                response.data, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            author = get_object_or_404(User, id=id)
            subscribe = Subscribe.objects.filter(user=self.request.user,
                                                 author=author)
            if subscribe.exists():
                subscribe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(SUBSCRIBE_NO_EXISTS,
                            status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет рецепта.
    Просмотр, создание, редактирование.
    """
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

    def add_recipe(self, request, pk, serializer):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_recipe(self, request, pk, model):
        model = model.objects.filter(
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk))
        if model.exists():
            model.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(request, pk,
                                   UserFavoritesSerializer)
        elif request.method == 'DELETE':
            return self.remove_recipe(request, pk, UserFavorites)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(request, pk,
                                   UserShoppingCartSerializer)
        elif request.method == 'DELETE':
            return self.remove_recipe(request, pk, UserShoppingCart)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcart__user=request.user
            )
            .order_by('ingredient__name')
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
        )
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
