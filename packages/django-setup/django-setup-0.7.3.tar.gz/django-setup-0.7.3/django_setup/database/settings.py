# -*- coding: utf-8 -*-
import dj_database_url
from django_setup import get_project_env_variable
################## SETTING DEFAULT DATABASE #############################
def get_databases(INSTALLED_APPS, default=True, other_dbs=None):
    DATABASES = {}
    if default:
        DEFAULT_DATABASE_URL = get_project_env_variable('DEFAULT_DATABASE_URL',
                            get_project_env_variable('DATABASE_URL'))
        DATABASES.update({'default':dj_database_url.parse(DEFAULT_DATABASE_URL)})
    if other_dbs:
        for db in other_dbs:
            db_url = get_project_env_variable('%s_DATABASE_URL' % db.upper())
            if db_url:
                DATABASES.update({db:dj_database_url.parse(db_url)})
    INSTALLED_APPS += ('south',)
    return INSTALLED_APPS, DATABASES
