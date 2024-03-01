# FoodGram - Продуктовый помощник
## Описание проекта:
Сайт FoodGram позволяет пользователям публиковать рецепты на своей странице, а также добавлять в избранное рецепты других авторов с возможностью подписаться на них.Главным приемуществом сайта является возможность добавить любой понравившийся рецепт в корзину покупок,а затем скачать список ингредиентов которые понадобятся для приготовления блюда.Благодаря нашему сайту у вас никогда не возникнет вопрос, что же приготовить своей семье на завтрак, обед или ужин.По тегам вы можете фильтровать блюда например: рецепты только для завтрака.
## Технологии :
* Python
* Django
* DjangoREST  
* PostgreSQL
* Nginx
* Gunicorn
* Docker
## Как развернуть проект

Клонируйте репозиторий:

```
git@github.com:Ekaterina110697/foodgram-project-react.git
```
В главное директории проекта создайте .env файл с данными:

```
POSTGRES_USER=имя пользователя БД
POSTGRES_PASSWORD=паоль от БД
POSTGRES_DB=название БД
DB_HOST=хост БД
DB_PORT=порт БД
DEBUG=False
SECRET_KEY= ваш секретный ключ django
ALLOWED_HOSTS=перечислите хосты через запятую на которых можно посмотреть сайт
```

Перейдите в папку infra:

```
cd infra
```

Запустите проект:

```
docker build up -d
```

Соберите статику:

```
docker compose exec backend python manage.py collectstatic 
```
Скорируйте статику в папку /static/:
 ```
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```
Выполните миграцию и заполните базу данных игредиентами:

```
docker-compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```
```
docker compose exec backend python manage.py import_csv
```
При необходимости создайте суперпользователя:
```
docker-compose  exec  web  python  manage.py  createsuperuser
```
## Проект можно посмотреть по адресу:
https://iambestcook.ddns.net/

## Автор проекта:
[Екатерина Курьянович](https://github.com/Ekaterina110697)

## Данные для входа администратора:
Почта
```
admin1@mail.ru
```
Пароль
```
12345qwe
```

Пароль
```
12345tat
```
