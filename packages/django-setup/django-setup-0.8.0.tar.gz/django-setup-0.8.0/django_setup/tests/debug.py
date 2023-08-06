# -*- coding: utf-8 -*-
'''
Created on Dec 9, 2012

@author: dudu
'''
import os
from django_setup.debug.settings import get_debug
from django_setup.tests import DjangoSetupTest

class Settings(DjangoSetupTest):
    
    def setUp(self):
        super(Settings, self).setUp('debug')
        
    def test_debug(self):
        #test default default
        debug = get_debug()
        self.assertTrue(debug)
        #test default
        debug = get_debug(default=False)
        self.assertFalse(debug)
        #test false and true value
        os.environ['DEBUG']='false'
        debug = get_debug()
        self.assertFalse(debug)
        os.environ['DEBUG']='tRuE'
        debug = get_debug(default=False)
        self.assertTrue(debug)
        #test project debug var precedence
        os.environ['DJANGOSETUP_DEBUG']='faLSE'
        debug = get_debug(default=False)
        self.assertFalse(debug)
        debug = get_debug()
        self.assertFalse(debug)