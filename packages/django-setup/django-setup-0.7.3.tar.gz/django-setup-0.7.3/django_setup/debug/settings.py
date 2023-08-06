# -*- coding: utf-8 -*-
from ast import literal_eval
from django_setup import get_project_env_variable

def get_debug(default=True):
    debug = get_project_env_variable('DEBUG', default)
    if isinstance(debug,basestring) and debug.lower() in ('true','false'):
        debug = literal_eval(debug.capitalize())
    return debug
