Cоздать виртуальное окружение:
```
python3 -m venv env
```
Активировать созданное виртуальное окружение:
```
source env/bin/activate
```
Выполните обновление инструмента установки пакетов pip для Python 3 на самую последнюю версию:
```
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Далее создадим проект foodgram:
```
django-admin startproject foodgram
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
Установите приложение users:
```
python  manage.py startapp users
```
Установите приложение users:
```
python  manage.py startapp users
```