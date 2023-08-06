# -*- coding: utf-8 -*-
'''
Created on Dec 8, 2012

@author: dudu
'''
import os
from django_setup.database.settings import get_databases
from django_setup.tests import DjangoSetupTest

class Settings(DjangoSetupTest):
    
    def setUp(self):
        super(Settings, self).setUp('database')
        self.installed_apps = ()
    def testDefaultDb(self):
        database_url = 'mysql://user:password@localhost/db1'
        os.environ['DATABASE_URL'] = database_url
        _installed_apps, DATABASES = get_databases(self.installed_apps)
        self.assertEqual(DATABASES['default']['NAME'], 'db1')
        self.assertEqual(len(DATABASES), 1)
        
        project_database_url = 'mysql://user:password@localhost/db2'
        os.environ['DJANGOSETUP_DATABASE_URL'] = project_database_url
        _installed_apps, DATABASES = get_databases(self.installed_apps)
        self.assertEqual(DATABASES['default']['NAME'], 'db2')
        self.assertEqual(len(DATABASES), 1)
        
        default_database_url = 'mysql://user:password@localhost/db3'
        os.environ['DEFAULT_DATABASE_URL'] = default_database_url
        _installed_apps, DATABASES = get_databases(self.installed_apps)
        self.assertEqual(DATABASES['default']['NAME'], 'db3')
        self.assertEqual(len(DATABASES), 1)
        
        project_default_database_url = 'mysql://user:password@localhost/db4'
        os.environ['DJANGOSETUP_DEFAULT_DATABASE_URL'] = project_default_database_url
        _installed_apps, DATABASES = get_databases(self.installed_apps)
        self.assertEqual(DATABASES['default']['NAME'], 'db4')
        self.assertEqual(len(DATABASES), 1)
        
    def testNonDefault(self):
        _installed_apps, DATABASES = get_databases(self.installed_apps, default=False)
        self.assertEqual(len(DATABASES), 0)
        
    def testOthers(self):
        database_url = 'mysql://user:password@localhost/db1'
        os.environ['DATABASE_URL'] = database_url
        database_url = 'mysql://user:password@localhost/db12'
        os.environ['DB1_DATABASE_URL'] = database_url
        database_url = 'mysql://user:password@localhost/db13'
        os.environ['DB2_DATABASE_URL'] = database_url
        _installed_apps, DATABASES = get_databases(self.installed_apps, other_dbs=['db1','db2'])
        self.assertEqual(len(DATABASES), 3)
        
    def testNoDb(self):
        self.assertRaises(AttributeError, get_databases, self.installed_apps)
        