DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MEDIA_URL = ''
STATIC_URL = ''

INSTALLED_APPS = (
    'content_links.tests',
    'content_links',
)
