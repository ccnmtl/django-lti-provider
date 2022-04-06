""" run tests for lti_provider

$ virtualenv ve
$ ./ve/bin/pip install Django
$ ./ve/bin/pip install -r test_reqs.txt
$ ./ve/bin/python runtests.py
"""


import django
from django.conf import settings
from django.core.management import call_command


def main():
    # Dynamically configure the Django settings with the minimum necessary to
    # get Django running tests
    settings.configure(
        SECRET_KEY="something super secret",
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
        MIDDLEWARE=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),

        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'lti_provider',
            'django_jenkins',
        ),
        TEST_RUNNER='django.test.runner.DiscoverRunner',

        AUTHENTICATION_BACKENDS=[
            'django.contrib.auth.backends.ModelBackend',
            'lti_provider.auth.LTIBackend',
        ],
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [
                    # insert your TEMPLATE_DIRS here
                ],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                        'django.template.context_processors.debug',
                        'django.template.context_processors.i18n',
                        'django.template.context_processors.media',
                        'django.template.context_processors.request',
                        'django.template.context_processors.static',
                        'django.template.context_processors.tz',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],
        COVERAGE_EXCLUDES_FOLDERS=['migrations'],
        ROOT_URLCONF='lti_provider.tests.urls',

        PROJECT_APPS=[
            'lti_provider',
        ],
        # Django replaces this, but it still wants it. *shrugs*
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
                'HOST': '',
                'PORT': '',
                'USER': '',
                'PASSWORD': '',
            }
        },
    )

    django.setup()

    # Fire off the tests
    call_command('test')
    call_command('jenkins', '--enable-coverage')

if __name__ == '__main__':
    main()
