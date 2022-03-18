### Проект YaTube:

Проект YaTube - это социальная сеть для публикации личных дневников. 
Позволяет пользователям создать свою страницу и публиковать на ней записи, просматривать страницы других пользователей и их записи, а также оставлять комментарии к постам.

### Технологии: 

Python 3, Django, Django ORM, pytest.


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/AlinaVoskoboynikova/hw05_final.git
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source venv/Scripts/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Создать суперпользователя:

```
python manage.py createsuperuser
``

Запустить проект:

```
python3 manage.py runserver
```

Примеры запросов:

Пример POST-запроса для аутентифицированного пользователя: добавление нового произведения. POST .../api/v1/titles/

```
{
    "name": "string",
    "year": 0,
    "description": "string",
    "genre": [
        "string"
    ],
    "category": "string"
}
```

Пример ответа:

```
{
    "id": 0,
    "name": "string",
    "year": 0,
    "rating": 0,
    "description": "string",
    "genre": [
       {}
    ],
    "category": {
        "name": "string",
        "slug": "string"
    }
}
```

Пример POST-запроса для аутентифицированного пользователя: добавление комментария к отзыву. POST .../api/v1/titles/{title_id}/reviews/{review_id}/comments/

```
{
    "text": "string"
}
```

Пример ответа:

```
{
    "id": 0,
    "text": "string",
    "author": "string",
    "pub_date": "2019-08-24T14:15:22Z"
}
```

Пример GET-запроса для любого пользователя: получение списка всех отзывов. GET .../api/v1/titles/{title_id}/reviews/


Пример ответа:

```
[
    {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": []
    }
]
```
