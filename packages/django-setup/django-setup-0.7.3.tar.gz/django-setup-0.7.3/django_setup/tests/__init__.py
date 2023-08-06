# -*- coding: utf-8 -*-
'''
Created on Dec 9, 2012

@author: dudu
'''
import os
from django.test import TestCase
from django_setup import set_project_name_variable

class DjangoSetupTest(TestCase):
    
    def setUp(self, substring):
        remove_vars = []
        for var in os.environ.iterkeys():
            if substring in var.lower():
                remove_vars.append(var)
        for var in remove_vars:
            os.environ.pop(var)
        set_project_name_variable('DJANGOSETUP')