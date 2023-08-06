# -*- coding: utf-8 -*-
def get_test_runner(INSTALLED_APPS, DATABASES, USE_CELERY=False):
    if USE_CELERY:
        TEST_RUNNER = 'django_setup.test.runner.DjangoSetupTestSuiteRunner'    
    else:
        TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    INSTALLED_APPS += ('django_nose',)
    for db in DATABASES.iterkeys():
        DATABASES[db]['ENGINE'] = 'django.db.backends.sqlite3'
        DATABASES[db]['NAME'] = '%s.db' % db
    SOUTH_TESTS_MIGRATE = False # To disable migrations and use syncdb instead 
    SKIP_SOUTH_TESTS = True # To disable South's own unit tests
    NOSE_ARGS = ['--match=^test', '--with-coverage',
                 '--with-yanc', '--cover-erase',
                 '--logging-level=INFO'] 
    return INSTALLED_APPS, DATABASES, TEST_RUNNER, SOUTH_TESTS_MIGRATE, SKIP_SOUTH_TESTS, NOSE_ARGS
