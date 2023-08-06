DATABASE_ENGINE = 'sqlite3'

SITE_ID = 1

SECRET_KEY = 'cb452188a1c017e94f96d9f813ec2bf8'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'proxylist',
]

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEST_RUNNER = 'discover_runner.DiscoverRunner'
USE_TZ = True

GRABBER_TIMEOUT = 5
GRABBER_CONNECT_TIMEOUT = 5
