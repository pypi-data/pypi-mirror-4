import re
from django_setup import get_project_name, get_project_env_variable
from django.conf import global_settings

def get_email(server_email=None, default_from_email=None, ignore_404s=None):
    EMAIL_SUBJECT_PREFIX = '[%s] ' % get_project_name()
    SERVER_EMAIL = server_email if server_email else global_settings.SERVER_EMAIL
    DEFAULT_FROM_EMAIL = default_from_email if default_from_email else global_settings.DEFAULT_FROM_EMAIL
    IGNORABLE_404_URLS = []
    if ignore_404s:
        for ignore_404 in ignore_404s:
            IGNORABLE_404_URLS.append(re.compile(ignore_404))
    return EMAIL_SUBJECT_PREFIX, SERVER_EMAIL, DEFAULT_FROM_EMAIL, IGNORABLE_404_URLS

def set_django_ses(INSTALLED_APPS):
    AWS_SES_ACCESS_KEY_ID = get_project_env_variable('AWS_SES_ACCESS_KEY_ID', None)
    AWS_SES_SECRET_ACCESS_KEY = get_project_env_variable('AWS_SES_SECRET_ACCESS_KEY', None)
    EMAIL_BACKEND = 'django_ses.SESBackend'
    INSTALLED_APPS += ('django_ses',)
    return INSTALLED_APPS, EMAIL_BACKEND, AWS_SES_ACCESS_KEY_ID, AWS_SES_SECRET_ACCESS_KEY
