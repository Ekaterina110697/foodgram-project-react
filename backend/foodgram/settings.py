import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost, 127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'rest_framework',
    'djoser',
    'django_filters',
    'colorfield',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'foodgram'),
        'USER': os.getenv('POSTGRES_USER', 'foodgram_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', 5432)
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']

}
AUTH_USER_MODEL = 'users.User'

DJOSER = {
    'SERIALIZERS': {
        'user_create': 'api.serializers.UserCreateSerializer',
        'user': 'api.serializers.UserProfileSerializer',
        'current_user': 'api.serializers.UserProfileSerializer',
    },
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user': ['rest_framework.permissions.AllowAny'],
    },
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
}
MAX_LEAGHT_NAME = 200
MAX_LEAGHT_MEASUREMENT_UNIT = 200
MAX_LEAGHT_COLOR = 7
MAX_LEAGHT_SLAG = 200
MIN_TIME_COOKING = 1
MAX_TIME_COOKING = 3600
MAX_LEAGHT_TEXT = 50
MIN_AMOUNT = 1
MAX_AMOUNT = 1000
PAGE_SIZE = 6
MAX_LEAGHT_EMAIL = 254
MAX_LEAGHT_USER_PARAMETRS = 150
INGRIDIENTS_FIELD = {'ingredients': 'Выберите пожалуйстя хотя бы 1 ингредиент'}
INGRIDIENTS_UNIQUE = {'ingredients': 'Выбранный вами ингредиент не является уникальным'}
INGRIDIENTS_NO_EXISTS = {'ingredients': 'Ингридиент не существует.'}
COUNT_AMOUNT = {'amount': 'Количество ингредиентов должно быть больше нуля'}
TAG_FIELD = {'tags': 'Выберите пожалуйстя хотя бы 1 тэг для рецепта'}
TAG_NO_EXISTS = {'tags': 'Тег не существует.'}
TAG_UNIQUE = {'tags': 'Выбранный вами тэг не является уникальным.'}
COUNT_COOKING_TIME = {'cooking_time': 'Время приготовления должно быть => 1 минуты'}
ERROR_SUBSCRIBE_HIMSELF = {'message': 'Вы не можете подписаться на самого себя'}
ERROR_SUBSCRIBE_ANOTHER_USER = {'message': 'Вы уже подписаны на данного пользователя'}
RECIPE_NOT_FOUND = {'errors': 'Рецепт не найден'}
RECIPE_EXISTS = {'errors': 'Рецепт уже добавлен в список'},
RECIPE_NO_IN_FAVORITE = {'errors': 'Рецепта нет в избранных.'}
RECIPE_NO_IN_SHOPPING_CART = {'errors': 'Рецепта нет в списке покупок.'}
SUBSCRIBE_EXISTS = {'errors': 'Вы подписаны на этого автора'}
SUBSCRIBE_NO_EXISTS = {'errors': 'Вы не подписаны на данного автора.'}
NEW_PASSWORD_NOT_VALID = {'errors': 'Введеные вами данные не корректны.'}
