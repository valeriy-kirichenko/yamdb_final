![example workflow](https://github.com/valeriy-kirichenko/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# Проект YaMDb :computer:
Описание проекта
----------
&ensp;&ensp;&ensp;&ensp;Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории. Список категорий может быть расширен.
&ensp;&ensp;&ensp;&ensp;Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
&ensp;&ensp;&ensp;&ensp;В каждой категории есть произведения: книги, фильмы или музыка. Произведению может быть присвоен жанр из списка предустановленных. Новые жанры может создавать только администратор.
&ensp;&ensp;&ensp;&ensp;Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти, из пользовательских оценок формируется усреднённая оценка произведения — рейтинг. На одно произведение пользователь может оставить только один отзыв.

[Развернутый проект](http://51.250.17.23/api/v1/)
----------

# Установка
Системные требования
----------
* Python 3.9+
* Works on Linux, Windows, macOS, BSD

Стек технологий
----------
* Python 3.9
* Django 2.2
* Django Rest Framework
* Docker
* Docker-compose
* PostgreSQL
* Pytest
* Simple-JWT

Запуск проекта
----------
Сперва установите [Docker](https://www.docker.com/get-started) и [Docker-compose](https://docs.docker.com/compose/install/), затем:
1. Клонируйте репозиторий, наберите в командной строке:
```bash
git clone 'git@github.com:valeriy-kirichenko/yamdb_final.git'
```
2. Переместитесь в папку /infra, создайте там файл .env и заполните его данными:
```bash
cd infra/
touch .env
nano .env
... # .env
SECRET_KEY= # Секретный ключ из settings.py
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER= # Придумайте пользователя
POSTGRES_PASSWORD= # Придумайте пароль
DB_HOST=db
DB_PORT=5432
# Ниже переменные необходимые для настройки отправки кода подтверждения при регистрации
EMAIL_HOST= # необходимо для отправки почты (прим. smtp.gmail.com)
EMAIL_HOST_USER= # почта_для_отправки_кода@gmail.com
EMAIL_HOST_PASSWORD= # пароль для приложения (настраивается в почте)
... # сохраните (Ctl + x)
```
3. Не выходя из /infra выполните команду:
```bash
docker-compose up -d
```
4. Выводим список запущенных контейнеров:
```bash
docker ps # нас интересует контейнер web, скопируйте его 'CONTAINER ID'
```
5. Зайдите в командную строку контейнера, выполните команду:
```bash
docker exec -it <CONTAINER ID> /bin/bash
```
6. Находясь в командной строке контейнера выполняем миграции, собираем статику:
```bash
python manage.py migrate
python manage.py collectstatic --no-input
```
7. При желании можете наполнить БД тестовыми данными, выполните команду:
```bash
python manage.py importcsv
```
----------
Автор:
----------
* **Кириченко Валерий Михайлович**
GitHub - [valeriy-kirichenko](https://github.com/valeriy-kirichenko)
----------
Документация к проекту с примерами запросов и ответов
----------
&ensp;&ensp;&ensp;&ensp;Документация для API [доступна по ссылке](http://localhost:8000/redoc/) после запуска приложения.
