from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipes.constants import (MAX_AMOUNT, MAX_LEAGHT_COLOR,
                               MAX_LEAGHT_MEASUREMENT_UNIT, MAX_LEAGHT_NAME,
                               MAX_LEAGHT_SLAG, MAX_LEAGHT_TEXT,
                               MAX_TIME_COOKING, MIN_AMOUNT, MIN_TIME_COOKING)

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиентов рецептов."""

    name = models.CharField(
        'Название ингредиента',
        max_length=MAX_LEAGHT_NAME,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LEAGHT_MEASUREMENT_UNIT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name} : {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов рецептов."""

    name = models.CharField(
        'Название тега',
        max_length=MAX_LEAGHT_NAME,
        unique=True
    )
    color = ColorField(
        'Цвет тега',
        max_length=MAX_LEAGHT_COLOR,
        unique=True
    )
    slug = models.SlugField(
        'Слаг тега',
        max_length=MAX_LEAGHT_SLAG,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} - {self.slug}'


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=MAX_LEAGHT_NAME,
    )
    image = models.ImageField(
        'Фото рецепта',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        'Ингредиенты',
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        'Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления блюда в минутах',
        validators=[
            MinValueValidator(
                MIN_TIME_COOKING,
                message=(
                    f'Минимальное время приготовления-{MIN_TIME_COOKING}минут'
                )
            ),
            MaxValueValidator(
                MAX_TIME_COOKING,
                message=(
                    f'Максимальное время приготовления-{MAX_TIME_COOKING}минут'
                )
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name} - {self.text[:MAX_LEAGHT_TEXT]}'


class RecipeIngredient(models.Model):
    """Модель количества ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                message=(
                    f'Минимальное количество ингредиентов -{MIN_AMOUNT}')),
            MaxValueValidator(
                MAX_AMOUNT,
                message=(
                    f'Максимальное количество ингредиентов -{MAX_AMOUNT}'))
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='ingredients_recipe_unique'
            )
        ]

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} - {self.amount}'


class UserRecipeList(models.Model):
    """Абстрактная модель для отображения рецепта
    в избранном и корзине покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('user', 'recipe')


class UserFavorites(UserRecipeList):
    """Список избранного пользователя"""

    class Meta(UserRecipeList.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='user_recipe_favorite_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class UserShoppingCart(UserRecipeList):
    """Список покупок пользавателя"""

    class Meta(UserRecipeList.Meta):
        verbose_name = 'Ингредиент для покупки'
        verbose_name_plural = 'Ингредиенты для покупки'
        default_related_name = 'shoppingcart'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='user_recipe_shoppingcart_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
