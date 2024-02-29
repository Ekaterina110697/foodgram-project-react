from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.settings import MAX_LEAGHT_EMAIL, MAX_LEAGHT_USER_PARAMETRS

from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=MAX_LEAGHT_EMAIL,
        unique=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LEAGHT_USER_PARAMETRS,
        unique=True,
        validators=[validate_username]
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LEAGHT_USER_PARAMETRS
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LEAGHT_USER_PARAMETRS
    )
    password = models.CharField(
        'Пароль',
        max_length=MAX_LEAGHT_USER_PARAMETRS
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='username_email_unique'
            )
        ]

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='publisher',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='subscribe_unique')
        ]

    def __str__(self):
        return f' Подписан {self.user} на {self.author}'
