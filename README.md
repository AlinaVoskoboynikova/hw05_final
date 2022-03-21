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
```

Запустить проект:

```
python3 manage.py runserver
```