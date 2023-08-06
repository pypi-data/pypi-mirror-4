# -*- coding: utf-8 -*-
'''
Created on Dec 9, 2012

@author: dudu
'''
from django_setup import get_project_env_variable

#def append_slash(string):
#    return '%s/' % string if string[-1] != '/' else string

def get_aws_domain(static_media, aws_bucket, default=None):
    aws_domain = 'AWS_%s_S3_DOMAIN' % static_media.upper()
    domain = get_project_env_variable(aws_domain, default)
    return aws_bucket if domain and domain.lower() == 'true'\
            else domain if domain\
            else '%s.s3.amazonaws.com' % aws_bucket
