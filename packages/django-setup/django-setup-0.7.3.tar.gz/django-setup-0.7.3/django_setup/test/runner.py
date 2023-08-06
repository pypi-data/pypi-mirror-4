# -*- coding: utf-8 -*-
'''
Created on Dec 9, 2012

@author: dudu
'''
from django_nose.runner import NoseTestSuiteRunner
from djcelery.contrib.test_runner import CeleryTestSuiteRunnerStoringResult

class DjangoSetupTestSuiteRunner(NoseTestSuiteRunner, CeleryTestSuiteRunnerStoringResult):
    pass
    

    
