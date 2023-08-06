# Django Vkontakte Places

<a href="https://travis-ci.org/ramusus/django-vkontakte-places" title="Django Vkontakte Places Travis Status"><img src="https://secure.travis-ci.org/ramusus/django-vkontakte-places.png"></a>

Приложение позволяет взаимодействовать с географическими объектами Вконтакте, такими как страны и города через Вконтакте API используя стандартные модели Django

## Установка

    pip install django-vkontakte-places

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'vkontakte_api',
        'vkontakte_places',
    )