#set project name variable
from django_setup import set_project_name_variable
#replace with your project name
project_name = set_project_name_variable('djangosetup')
INSTALLED_APPS = ()
################## DEBUG ###############################################
from django_setup.debug.settings import get_debug
DEBUG = get_debug()
################## DATABASES ###########################################
from django_setup.database.settings import get_databases
INSTALLED_APPS, DATABASES = get_databases(INSTALLED_APPS)
################## STATIC AND MEDIA FOR AWS S3 #########################
from django_setup.aws_s3.settings import get_static_media_settings
INSTALLED_APPS, STATIC_URL, STATICFILES_STORAGE, \
MEDIA_URL, MEDIA_ROOT, DEFAULT_FILE_STORAGE,\
AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY,\
AWS_HEADERS, AWS_PRELOAD_METADATA,\
AWS_STATIC_S3_BUCKET, AWS_STATIC_S3_DOMAIN, AWS_STATIC_S3_SECURE,\
AWS_MEDIA_S3_BUCKET, AWS_MEDIA_S3_DOMAIN, AWS_MEDIA_S3_SECURE = get_static_media_settings(INSTALLED_APPS)
################## TEST RUNNED#########################################
from django_setup.test.settings import get_test_runner
INSTALLED_APPS, DATABASES, TEST_RUNNER, SOUTH_TESTS_MIGRATE, SKIP_SOUTH_TESTS, NOSE_ARGS = get_test_runner(INSTALLED_APPS, DATABASES)
#add options from django-coverage and django-nose
