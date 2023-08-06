# -*- coding: UTF-8 -*-
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve
from django.contrib.auth import authenticate
from django.utils import simplejson
from django.contrib.auth.models import AnonymousUser

class Class():
    
    def __init__(self, *args, **kwargs):
        for k,v in kwargs.iteritems():
            setattr(self, k, v)

class FactoryTest(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def get_user(self, credentials):
        if isinstance(credentials, tuple) or isinstance(credentials, list):
            username, password = credentials 
            credentials = {'username':username,\
                           'password':password}
        #otherwise, we assume it's a dict already
        return authenticate(**credentials)
    
class UrlTest(TestCase):
          
    def request(self, path, data={}, ajax=False):
        method = 'post' if data or ajax else 'get'
        kwargs = {'path':path}
        if data:
            kwargs['data']=data
        if ajax:
            kwargs['HTTP_X_REQUESTED_WITH']='XMLHttpRequest'
        return getattr(self.client, method)(**kwargs)
    
    def verify_response(self, response, templates=[],
                        view_name=None, status_code=200):
        self.assertEqual(response.status_code, status_code)
        for template_name in templates:
            self.assertTemplateUsed(response, template_name, 
                    'Template Not Used: %s' % template_name)
        self.verify_view(response, view_name)
 
    def request_response(self, path, data={}, ajax=False, 
                         templates=[], view_name=None,
                         status_code=200):
        response = self.request(path, data, ajax)
        self.verify_response(response, templates, 
                             view_name, status_code)

    def verify_view(self, response, view_name):
        if view_name:
            self.assertEqual(resolve(response.request\
                                     ["PATH_INFO"])\
                             [0].func_name,\
                             view_name)        

    def request_redirect(self, path, data={}, ajax=False,
                         view_name=None, expected_url=None,
                         status_code=302, target_status_code=200):
        response = self.request(path, data, ajax)
        self.verify_view(response, view_name)
        self.assertRedirects(response, expected_url, status_code,
                             target_status_code)

class AdminTest(UrlTest):
    
    @property
    def app(self):
        return self.__class__.app
    
    @property
    def base_url(self):
        return '/admin/%s' % self.app
    
    def change_list_test(self, model):
        templates = ['admin/change_list.html',
                     'admin/base_site.html',
                     'admin/base.html']
        path = '%s/%s/' % (self.base_url, model)
        view_name = 'changelist_view'
        self.request_response(path, templates=templates, view_name=view_name)
        
    def change_form_test(self, model, instance_id):
        templates = ['admin/change_form.html', 
                     'admin/base_site.html', 
                     'admin/base.html',
                     'admin/includes/fieldset.html']
        path = '%s/%s/%s/' % (self.base_url, model, instance_id)
        view_name = 'change_view'
        self.request_response(path, templates=templates, view_name=view_name)

class ViewTest(FactoryTest):
    
    def request(self, path, view, data={}, ajax=False,
                credentials = None, arguments = {}):
        method = 'post' if data or ajax else 'get'
        kwargs = {'path':path}
        if data:
            kwargs['data']=data
        if ajax:
            kwargs['HTTP_X_REQUESTED_WITH']='XMLHttpRequest'
        request = getattr(self.factory, method)(**kwargs)
        if credentials:
            user = self.get_user(credentials)
            request.user = user
        else:
            request.user = AnonymousUser()
        return view(request, **arguments)
    
    def verify_response(self, response, contain_list = [],
                        not_contain_list=[], status_code=200):
        
        self.assertEqual(response.status_code, status_code)
        for contain in contain_list:
            self.assertContains(response, **contain)
        for not_contain in not_contain_list:
            self.assertNotContains(response, **not_contain)
            
    def request_response(self, path, view, data={}, ajax=False,
                         credentials = None, arguments = {},
                         contain_list=[], not_contain_list=[],
                         status_code=200):
        response = self.request(path, view, data, ajax,
                                credentials, arguments)
        self.verify_response(response, contain_list,
                             not_contain_list, status_code)
    
class AjaxTest(ViewTest):
        
    def request(self, path, view, data={},
                credentials = None, arguments = {}):
        return super(AjaxTest, self).request(path, view[0], data,
                    True, credentials, arguments)
    
    def verify_dajax_response(self, json_response_string, dajax_data):
        json_response = simplejson.loads(json_response_string)
        self.assertEqual(len(dajax_data), len(json_response))
        for dajax, json in zip(dajax_data, json_response):
            self.assertDictEqual(dajax, json)

    def request_response(self, path, view, data={},
                         credentials = None, arguments = {},
                         dajax_data = []):
        response = self.request(path, view, data,
                                credentials, arguments)
        self.verify_dajax_response(response, dajax_data)
