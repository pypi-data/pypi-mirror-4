# Django Vkontakte Places

Приложение позволяет взаимодействовать с географическими объектами Вконтакте, такими как страны и города через Вконтакте API используя стандартные модели Django

## Установка

    pip install django-vkontakte-places

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'vkontakte_api',
        'vkontakte_places',
    )