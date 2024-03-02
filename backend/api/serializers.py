from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from api.constants import (INGRIDIENTS_FIELD, INGRIDIENTS_UNIQUE, TAG_FIELD,
                           TAG_UNIQUE, RECIPE_EXISTS, ERROR_SUBSCRIBE_HIMSELF,
                           SUBSCRIBE_EXISTS)
from api.utils import Base64ImageField
from recipes.models import (Ingredient, Recipe, RecipeIngredient, Tag,
                            UserFavorites, UserShoppingCart)
from users.models import Subscribe

User = get_user_model()


class UserProfileSerializer(UserSerializer):
    """Сериализатор для просмотра страницы пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscribe.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        )


class RecipeSubscribesSerializer(serializers.ModelSerializer):
    """Серилизатор для просмотра рецепта в подписках """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribesListSerializer(UserProfileSerializer):
    """Серилизатор для просмотра подписок """
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj).all()
        if limit:
            recipes = recipes[: int(limit)]
        return RecipeSubscribesSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class AddRemoveSubcribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(ERROR_SUBSCRIBE_HIMSELF)
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(SUBSCRIBE_EXISTS)
        return data


class IngredientsSerializer(serializers.ModelSerializer):
    """ Сериализатор для ингридиентов. """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели, связывающей ингредиенты и рецепт."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор связывающей ингредиенты и их колличество ."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    ingredients = RecipeIngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        """Проверка корректности заполенния поля ингридиентов."""
        if not ingredients:
            raise serializers.ValidationError(INGRIDIENTS_FIELD)
        ingredient_id = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_id) != len(set(ingredient_id)):
            raise serializers.ValidationError(INGRIDIENTS_UNIQUE)
        return ingredients

    def validate_tags(self, tags):
        """Проверка корректности заполенния поля тэг."""
        if not tags:
            raise ValidationError(TAG_FIELD)
        if len(tags) > len(set(tags)):
            raise ValidationError(TAG_UNIQUE)
        return tags

    def create_ingredients(self, ingredients, recipe):
        """Создает новый ингридиет."""
        create_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(
            create_ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        """Создает новый рецепт."""
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        if 'ingredients' not in validated_data or 'tags' not in validated_data:
            raise serializers.ValidationError('Поле не может быть пустым.')
        ingredient = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredients(ingredient, instance)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращает сериализованный экземпляр рецепта."""
        return ReadRecipeSerializer(
            instance,
            context=self.context
        ).data


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserProfileSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredient')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and UserFavorites.objects.filter(
                   user=request.user,
                   recipe=obj
                ).exists()
                )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and UserShoppingCart.objects.filter(
                   user=request.user,
                   recipe=obj
                ).exists()
                )


class UserShoppingCartSerializer(serializers.ModelSerializer):
    """Cериализатор для списка покупок."""
    class Meta:
        model = UserShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if UserShoppingCart.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(RECIPE_EXISTS)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSubscribesSerializer(
            instance.recipe,
            context={'request': request}).data


class UserFavoritesSerializer(serializers.ModelSerializer):
    """Cериализатор для избранного."""
    class Meta:
        model = UserFavorites
        fields = ('user', 'recipe')

    def validate(self, data):
        if UserFavorites.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(RECIPE_EXISTS)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSubscribesSerializer(
            instance.recipe,
            context={'request': request}).data
