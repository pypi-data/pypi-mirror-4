Django Google Tools
===================

.. image:: https://secure.travis-ci.org/camilonova/django-google-tools.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/camilonova/django-google-tools

Django app for managing Google Analytics and Site Verification codes.


Installation
------------

In your virtualenv just type::

    $ pip install django-google-tools


Configuration
-------------

1. Add ``googletools`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'googletools',
        ...
    )

2. Run in your shell::

    $ ./manage.py syncdb

Or if you are using ``South``::

    $ ./manage.py migrate

If you have in your settings ``DEBUG=True`` googletools will not render anything
because this library is inteded mostly to use on production sites, if you want to
change this behavior you can set ``GOOGLETOOLS_ENABLED=True`` in your settings
file. Just for clarification it is defined like this::

    GOOGLETOOLS_ENABLED = not DEBUG

This means, by default googletools will be enabled when ``DEBUG=False``.


Management
----------

Go to the admin interface. When correctly installed, you will find the
*Googletools* app. There you can manage your Google Analytics and Site Verification
codes.


Templatetags
------------

In order to use the googletools in your templates you'll have to load the templatetags.

``{% load googletools %}``

Use ``{% analytics_code %}`` for inserting your Analytics code.

Use ``{% site_verification_code %}`` for inserting your site verification code.

Templatetags will return an empty string if they are not configured for the current site.

The template should look like::

    {% load googletools %}
    <html>
        <head>
            <meta charset="utf-8">
            ...
            <meta name="description" content="..." />
            {% site_verification_code %}

            <link rel="stylesheet" href="/static/css/style.min.css">

            {% analytics_code %}
        </head>
        <body>
            <h1>My awesome project</h1>
            ...
        </body>
    </html>
