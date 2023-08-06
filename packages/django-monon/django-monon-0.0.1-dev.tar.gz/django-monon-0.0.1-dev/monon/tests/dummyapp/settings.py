DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db',
    }
}
INSTALLED_APPS = (
    'monon',
    'monon.tests.dummyapp'
)
SITE_ID = 1
SECRET_KEY = 'this-is-just-for-tests-so-not-that-secret'
