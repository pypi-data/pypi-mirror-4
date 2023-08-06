import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'discover_runner',
    'geetar',
    'test_app',
)

SECRET_KEY = "geetarT3st!"

TEST_RUNNER = 'discover_runner.DiscoverRunner'

TEST_DISCOVER_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tests')

GOOGLE_MAPS_API_KEY = 'AIzaSyCuJe82BXhTESkKmlo3V4Rft_IsxGhJwDU'