# Интернет-магазин MEGANO
Владелец торгового центра во время COVID-карантина решил перевести своих арендодателей в онлайн. Сделать это он намерен с помощью создания платформы, на которой продавцы смогут разместить информацию о себе и своём товаре. Онлайновый торговый центр или, другими словами, интернет-магазин, являющийся агрегатором товаров различных продавцов.

## Как установить
Для работы микросервиса нужен Python версии не ниже 3.10 и установленное ПО для контейнеризации - [Docker](https://docs.docker.com/engine/install/).    

Настройка переменных окружения  
1. Скопируйте файл .env.dist в .env
2. Заполните .env файл. Пример:  
```yaml
DATABASE_URL = postgresql://skillbox:secret@127.0.0.1:5434/market
REDIS_URL = redis://127.0.0.1:6379/0
PAY_URL = http://127.0.0.1:8000/pay
```

Запуск СУБД Postgresql
```shell
docker run --name skillbox-db -e POSTGRES_USER=skillbox -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=market -p 5434:5432 -d postgres
```
Запуск брокера сообщений REDIS
```shell
docker run --name redis-db -p 6379:6379 -d redis
```
Установка виртуального окружения для среды разработки на примере ОС Windows
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements\dev.txt
```
Установка виртуального окружения для продовой среды на примере ОС Linux
```shell
python -m venv venv
. venv/bin/activate
pip install -r requirements/base.txt
```  

Загрузить все фикстуры
```shell
python run_fixtures.py
```
Использование Black
```
    black <путь к файлу или директория> - чтобы редактировать код через black
    Если вы не хотите, чтобы ваш код был отредактирован, обернуть в #fmt: off <ваш код> #fmt: on. 
    (#fmt: off/on определяется как комментарий)
```
### Как удалить контейнеры
СУБД Postgres  
```
 docker rm -f -v skillbox-db
```

Брокер сообщений REDIS  
```
 docker rm -f -v redis-db
```

## Проверка форматирования кода
Проверка кода выполняется из корневой папки репозитория.    
* Анализатор кода flake8  
```shell
flake8
```
* Линтер pylint  
```shell
pylint --rcfile=.pylintrc market/* 
```

## Как запустить web-сервер
Запуск сервера производится в активированном локальном окружение из папки `market/`
```shell
python manage.py runserver 0.0.0.0:8000
```

# Цели проекта

Код написан в учебных целях — это курс по Джанго на сайте [Skillbox](https://go.skillbox.ru/education/course/django-framework).  
