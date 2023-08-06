__version__ = '0.7.3'
__author__ = 'Eduardo S. Klein'
__email__ = 'duduklein@gmail.com'
__url__ = 'http://bitbucket.org/eduardoklein/django-setup/'

import os

def set_project_name_variable(project_name):
    project = project_name.upper()
    os.environ['DJANGO_SETUP_PROJECT_NAME'] = project
    return project

def get_project_name():
    PROJECT_NAME = os.environ.get('DJANGO_SETUP_PROJECT_NAME',None)
    return '%s' % PROJECT_NAME.upper() if PROJECT_NAME else ''

def get_project_env_variable(variable, default=None):    
    project_name = get_project_name()
    project_variable = '%s_%s' % (project_name, variable)
    return os.environ.get(project_variable, os.environ.get(variable,default))

