# "Продуктовый помощник" (Проект «Фудграм»)

## 1. [Описание](#1)
## 2. [Стек технологий проекта](#2)
## 3. [Запуск проекта в Docker контейнерах с помощью Docker Compose](#3)
## 4. [Ссылка на развернутый проект](#4) 
## 5. [Автор проекта:](#5)

---

## 1. Описание <a id=1></a>

Проект "Продуктовый помощник" (Проект «Фудграм») предоставляет пользователям следующие возможности:
  - регистрироваться любому пользователю
  - создавать свои рецепты и возможность работы с ними (т.е. добавлять\корректировать\удалять)
  - просматривать рецепты других пользователей (доступно всем пользователям)
  - добавлять рецепты других пользователей в разделы: "Избранное" и в "Корзину"
  - подписываться на других пользователей (доступно авторизованным пользователям)
  - скачать список ингредиентов для рецептов, добавленных в "Корзину" (PDF-форма)

---

## 2. Стек технологий проекта <a id=2></a>
[![Django](https://img.shields.io/badge/Django-4.2.1-6495ED)](https://www.djangoproject.com) 
[![Djangorestframework](https://img.shields.io/badge/djangorestframework-3.14.0-6495ED)](https://www.django-rest-framework.org/) 
[![Django Authentication with Djoser](https://img.shields.io/badge/Django_Authentication_with_Djoser-2.2.0-6495ED)](https://djoser.readthedocs.io/en/latest/getting_started.html) 
[![Nginx](https://img.shields.io/badge/Nginx-1.21.3-green)](https://nginx.org/ru/) 
[![React](https://img.shields.io/badge/React-18.2.0-6495ED)](https://react.dev/) 
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-6495ED)](https://www.postgresql.org/)

- Веб-сервер: nginx (контейнер nginx)  
- Frontend фреймворк: React (контейнер frontend)  
- Backend фреймворк: Django (контейнер backend)  
- API фреймворк: Django REST (контейнер backend)  
- База данных: PostgreSQL (контейнер db)

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.  
Контейнер nginx взаимодействует с контейнером backend через gunicorn.  
Контейнер frontend взаимодействует с контейнером backend посредством API-запросов и передачи информации на фронтенд.


## 3. Запуск проекта в Docker контейнерах с помощью Docker Compose <a id=3></a>

Склонируйте проект из репозитория:
```bash
git clone git@github.com:DPavlen/foodgram-project-react.git
```
Перейдите в директорию проекта kittygram_final:
```bash
cd foodgram-project/
```
Создайте файл .env для PostgreSQL в корне проекта и контейнера backend, впишите в него переменные для инициализации БД и связи с ней. Затем добавьте строки, содержащиеся в файле .env.example и подставьте свои значения.
Пример из файла с расширением .env:
```bash
# Мы используем СУБД PostgreSQL, необходимо заполнить следующие константы.
POSTGRES_USER=your_django_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=db_name
# Добавляем переменные для Django-проекта:
DB_HOST=db
DB_PORT=port_for_db  # Default is 5432
# Настройки настройки переменных settings
SECRET_KEY=DJANGO_SECRET_KEY  # Your django secret key 'django-insecure......'
DEBUG=True # Set to True if you do need Debug.
ALLOWED_HOSTS=127.0.0.1 # localhost by default if DEBUG=False
```
Запустите Docker Compose с этой конфигурацией на своём компьютере. Название файла конфигурации надо указать явным образом, ведь оно отличается от дефолтного. Имя файла указывается после ключа -f:
```bash
docker compose -f docker-compose.production.yml up
```
Команда описанная выше, сбилдит Docker образы и запустит backend, frontend, СУБД и Nginx в отдельных Docker контей.
Выполните миграции в контейнере с backend и необходимо собрать статику backend'a, поочередно выполните 2 команды:
```bash
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
```
Создать суперюзера (Администратора):
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

Переместите собранную статику в volume(Данные можно сохранить отдельно от контейнера: для этого придумали Docker volume), 
созданный Docker Compose для хранения статики:
```bash
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /static/static/
```
По завершении всех операции проект будет запущен и доступен по адресу:
```bash
http://127.0.0.1/
```
Останавливает все сервисы, связанные с определённой конфигурацией Docker Compose. 
Для остановки Docker контейнеров выполните следующую команду в корне проекта:
```bash
sudo docker compose -f docker-compose.yml down
```

## 4. Ссылка на развернутый проектe <a id=4></a>
Ссылка на развернутый проектe https://foodgrampavlen.hopto.org/recipes 

---
## 5. Автор проекта: <a id=5></a> 
**Павленко Дмитрий**
- Ссылка на мой профиль в GitHub [Dmitry Pavlenko](https://github.com/DPavlen)
