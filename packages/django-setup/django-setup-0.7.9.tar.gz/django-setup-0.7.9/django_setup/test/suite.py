# -*- coding: UTF-8 -*-
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve
from django.contrib.auth import authenticate
from django.utils import simplejson
from django.contrib.auth.models import AnonymousUser
from django.db.utils import IntegrityError
from urlparse import urlsplit, urlunsplit


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
                        view_name=None, contain_list=[],
                        not_contain_list=[], status_code=200):
        self.assertEqual(response.status_code, status_code)
        for template_name in templates:
            self.assertTemplateUsed(response, template_name, 
                    'Template Not Used: %s' % template_name)
        self.verify_view(response, view_name)
        for contain in contain_list:
            self.assertContains(response, **contain)
        for not_contain in not_contain_list:
            self.assertNotContains(response, **not_contain)
            
    def request_response(self, path, data={}, ajax=False, 
                         templates=[], view_name=None,
                         contain_list=[], not_contain_list=[],
                         status_code=200):
        response = self.request(path, data, ajax)
        self.verify_response(response=response, templates=templates, 
                             view_name=view_name, contain_list=contain_list,
                             not_contain_list=not_contain_list,
                             status_code=status_code)
        return response

    def verify_view(self, response, view_name):
        if view_name:
            self.assertEqual(resolve(response.request\
                                     ["PATH_INFO"])\
                             [0].func_name,\
                             view_name)        

    def request_redirect(self, path, data={}, ajax=False,
                         view_name=None, expected_url=None,
                         status_code=302, form=None):
        response = self.request(path, data, ajax)
        self.verify_view(response, view_name)
        if form:
            self.assert_form_redirect(response,
                                      expected_url,
                                      form, status_code)
        else:
            self.assert_redirect_no_follow(response,
                                           expected_url,
                                           status_code)
        return response

    def assert_redirect_no_follow(self, response, expected_url,
                    status_code = 302, host=None, msg_prefix=''):
        if msg_prefix:
            msg_prefix += ": "
        self.assertEqual(response.status_code, status_code,
                msg_prefix + "Response didn't redirect as expected: Response"
                " code was %d (expected %d)" %
                    (response.status_code, status_code))
        url = response['Location']
        e_scheme, e_netloc, e_path, e_query, e_fragment = urlsplit(
                                                              expected_url)
        if not (e_scheme or e_netloc):
            expected_url = urlunsplit(('http', host or 'testserver', e_path,
                e_query, e_fragment))

        self.assertEqual(url, expected_url,
            msg_prefix + "Response redirected to '%s', expected '%s'" %
                (url, expected_url))

    def assert_form_redirect(self, response, expected_url, form = 'form',
                             status_code = 302):
        if response.status_code == 200:
            context_form = response.context_data[form]
            msgs = ['Response did not redirect as expected']
            for field, error in context_form.errors.iteritems():
                msgs.append('%s: %s' % (field, error.as_text()))
            self.fail('\n'.join(msgs))
        else:
            self.assert_redirect_no_follow(response, expected_url, status_code)
        
class AdminTest(UrlTest):

    @property
    def app(self):
        return self.__class__.app

    @property
    def base_url(self):
        return '/admin/%s' % self.app

    def change_list_test(self, model, **kwargs):
        templates = ['admin/change_list.html',
                     'admin/base_site.html',
                     'admin/base.html']
        path = '%s/%s/' % (self.base_url, model)
        view_name = 'changelist_view'
        return self.request_response(path, templates=templates,
                                     view_name=view_name, **kwargs)

    def change_form_test(self, model, instance_id, **kwargs):
        templates = ['admin/change_form.html', 
                     'admin/base_site.html', 
                     'admin/base.html',
                     'admin/includes/fieldset.html']
        path = '%s/%s/%s/' % (self.base_url, model, instance_id)
        view_name = 'change_view'
        return self.request_response(path, templates=templates,
                                     view_name=view_name, **kwargs)

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
        return response

class AjaxTest(ViewTest):

    def request(self, path, view, data={},
                credentials = None, arguments = {}):
        view = view[0] if hasattr(view,'__iter__') else view
        json_response_string = super(AjaxTest, self).request(path, view, data,
                                                True, credentials, arguments) 
        return simplejson.loads(json_response_string)

    def verify_dajax_response(self, json_response, dajax_data, indexes=None):
        self.assertEqual(len(dajax_data), len(json_response))
        if indexes is not None:
            if indexes is True:
                indexes = range(len(dajax_data))
            for i, (dajax, json) in enumerate(zip(dajax_data, json_response)):
                if i in indexes: 
                    self.assertDictEqual(dajax, json)

    def request_response(self, path, view, data={},
                         credentials = None, arguments = {},
                         dajax_data = [], indexes=None):
        response = self.request(path, view, data,
                                credentials, arguments)
        self.verify_dajax_response(response, dajax_data, indexes=indexes)
        return response

class ModelsTest(TestCase):

    def verify_natural_keys(self, models):
        for Model in models:
            obj = Model.objects.all()[0]
            self.verify_natural_key_for_object(obj)

    def verify_natural_key_for_object(self, obj):
        nk = obj.natural_key()
        Model = obj.__class__
        self.assertEqual(Model.objects.get_by_natural_key(*nk), obj)
        obj.pk=None
        self.assertRaises(IntegrityError, obj.save)
