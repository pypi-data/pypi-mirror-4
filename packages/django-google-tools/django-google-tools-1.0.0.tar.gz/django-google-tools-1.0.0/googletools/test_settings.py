DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.sites',
    'googletools',
]

SECRET_KEY = 'secret'
