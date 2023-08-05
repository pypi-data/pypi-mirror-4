django-url-fullpath-redirect
==================

``django-url-fullpath-redirect`` - простой приложение для редиректов в Django. Форк проекта django-url-tracker.
Поддерживает на данный момент следующие коды ответа:
1. 304
2. 410
Редиректы задаются через админку

Установка
------------

Просто::

    pip install django-url-fullpath-redirect

Настройка
-------------

Для запуска добавляем в ``settings.py``:

1. Ставим последним в ``MIDDLEWARE_CLASSES`` наше ``url_tracker.middleware.URLChangePermanentRedirectMiddleware``::

        MIDDLEWARE_CLASSES = (
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
            'url_tracker.middleware.URLChangePermanentRedirectMiddleware',
        )

2. И добавляем в ``INSTALLED_APPS`` ::

       INSTALLED_APPS = (
            "url_tracker",
       )



Теперь обновляем базу и можем задавать редиректы через админку.
Профит.
