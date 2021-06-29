# [Социальная сеть Yatube](http://130.193.52.82/)

Это онлайн-сервис, где пользователи смогут публиковать публиковать интересные сообщения и картинки, подписываться на любимых авторов, оставлять комментарии и добавлять посты к группам.

## Что умеет социальная сеть:
- Администрирование
- Регистрация новых пользователей
- Создание, редактирование, удаление и комментирование постов
- Возможность подписки на интересных авторов

## Запуск приложения:
1) [Установите Docker](https://www.docker.com/products/docker-desktop)
2) Клонируйте репозиторий с проектом:
```
git clone https://github.com/sidorenkov-v-a/Yatube.git
```
3) В корневой директории проекта создайте файл `.env`, в котором пропишите переменные окружения  
>Список необходимых переменных можно найти в файле `.env.example`
4) Перейдите в директорию проекта и запустите приложение
```
docker-compose up
```
5) Дополнительные возможности:
- Войдите в контейнер
```
docker exec -it yatube_web_1 bash
```
- Создайте суперпользователя
```
python manage.py createsuperuser
```
- Используйте тестовые данные
```
python manage.py loaddata dump.json
```

## Стек технологий:   
- Django framework 3.0.5
- Django rest framework 3.11.0
- Pillow
- PostgreSQL 12.4
- Gunicorn 20.04
- Nginx 1.19.0
- Docker, docker-compose
- Проект запущен на сервере Yandex.cloud

#### Об авторе:
[Профиль Github](https://github.com/sidorenkov-v-a/)  
[Telegram](https://t.me/sidorenkov_vl)
