import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from foodgram.settings import (COUNT_AMOUNT, COUNT_COOKING_TIME,
                               ERROR_SUBSCRIBE_ANOTHER_USER,
                               ERROR_SUBSCRIBE_HIMSELF, INGRIDIENTS_FIELD,
                               INGRIDIENTS_NO_EXISTS, INGRIDIENTS_UNIQUE,
                               MIN_AMOUNT, MIN_TIME_COOKING, TAG_FIELD,
                               TAG_NO_EXISTS, TAG_UNIQUE)
from recipes.models import (Ingredient, Recipe, RecipeIngredient, Tag,
                            UserFavorites, UserShoppingCart)
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from users.models import Subscribe, User


class Base64ImageField(serializers.ImageField):
    """Сериализатор для кодирования и декодирования изображения."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя с обязательными полями."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class UserProfileSerializer(UserSerializer):
    """Сериализатор для просмотра страницы пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscribe.objects.filter(user=user, author=obj).exists()
        return False


class RecipeSubscribesSerializer(serializers.ModelSerializer):
    """Серилизатор для просмотра рецепта в подписках """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserPasswordSerializer(serializers.Serializer):
    """Серилизатор для смены пароля """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class SubscribesListSerializer(serializers.ModelSerializer):
    """Серилизатор для просмотра подписок """
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscribe.objects.filter(author=obj, user=user).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj).all()
        if limit:
            recipes = recipes[: int(limit)]
        return RecipeSubscribesSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def validate_subscribe(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise ValidationError(ERROR_SUBSCRIBE_HIMSELF)
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(ERROR_SUBSCRIBE_ANOTHER_USER)
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
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор связывающей ингредиенты и их колличество ."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    ingredients = RecipeIngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

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
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(INGRIDIENTS_FIELD)
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(INGRIDIENTS_NO_EXISTS)
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(INGRIDIENTS_UNIQUE)
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) < MIN_AMOUNT:
                raise serializers.ValidationError(COUNT_AMOUNT)
        return ingredients

    def validate_tags(self, tags):
        """Проверка корректности заполенния поля тэг."""
        tags_list = []
        if not tags:
            raise ValidationError(TAG_FIELD)
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(TAG_NO_EXISTS)
            if tag.id in tags_list:
                raise ValidationError(TAG_UNIQUE)
            tags_list.append(tag.id)
        return tags

    def validate_cooking_time(self, cooking_time):
        """Проверка корректности времени приготовления блюда."""
        if cooking_time < MIN_TIME_COOKING:
            raise serializers.ValidationError(COUNT_COOKING_TIME)
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        """Создает новый ингридиет."""
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient_id=ingredient_id, amount=amount
            )

    def create(self, validated_data):
        """Создает новый рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

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
    ingredients = serializers.SerializerMethodField(read_only=True)
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
        user = self.context.get('request').user
        if user.is_authenticated:
            return UserFavorites.objects.filter(recipe=obj, user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return UserShoppingCart.objects.filter(
                recipe=obj,
                user=user
            ).exists()
        return False


class UserShoppingCartSerializer(serializers.ModelSerializer):
    """Cериализатор для списка покупок."""
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserFavoritesSerializer(serializers.ModelSerializer):
    """Cериализатор для избранного."""
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
