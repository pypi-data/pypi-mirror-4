import os

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

DEBUG = True
DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}
MIDDLEWARE_CLASSES= ('django.middleware.common.CommonMiddleware',
         'django.contrib.sessions.middleware.SessionMiddleware',
          'django.middleware.csrf.CsrfViewMiddleware',
           'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',)

INSTALLED_APPS=(
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'south',
    'feedback',
    'django_nose',
)
SITE_ID=1
ROOT_URLCONF = 'example_project.urls'
SECRET_KEY='this-is-just-for-tests-so-not-that-secret'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEMPLATE_DIRS = [PROJECT_PATH + '/templates']
STATIC_URL = "/static/" 
