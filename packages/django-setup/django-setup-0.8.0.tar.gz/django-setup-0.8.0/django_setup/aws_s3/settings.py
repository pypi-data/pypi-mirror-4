from django.conf import global_settings
from django_setup import get_project_env_variable
from django_setup.aws_s3.utils import get_aws_domain
                
################ STATIC AND MEDIA FILES STORAGE AND URL ###############
#AWS CREDENTIALS
def set_aws_s3(INSTALLED_APPS):
    AWS_S3_ACCESS_KEY_ID = get_project_env_variable('AWS_S3_ACCESS_KEY_ID',None)
    AWS_S3_SECRET_ACCESS_KEY = get_project_env_variable('AWS_S3_SECRET_ACCESS_KEY',None)
    
    FARFUTURE_HEADERS =  get_project_env_variable('FARFUTURE_HEADERS',False)
    AWS_IS_GZIPPED = get_project_env_variable('AWS_IS_GZIPPED',False)
    #set the html headers to "far future" in order to cache them locally
    #only use it if you use a versioning control of you static files
    #also, you a function to change your media upload files to make them unique
    AWS_HEADERS = {}
    if FARFUTURE_HEADERS and FARFUTURE_HEADERS.lower() == 'true':
        AWS_HEADERS['Expires']='Thu, 15 Apr 2110 20:00:00 GMT'
        AWS_HEADERS['Cache-Control']='public, max-age=31536000'
    INSTALLED_APPS += ('storages',)
    return INSTALLED_APPS, AWS_S3_ACCESS_KEY_ID, \
            AWS_S3_SECRET_ACCESS_KEY, AWS_HEADERS, AWS_IS_GZIPPED

def get_static_settings():
    ##################  STATIC FILES  ##################################
    #Set AWS_PRELOAD_METADATA to True in order to only upload modified files to S3
    AWS_PRELOAD_METADATA = get_project_env_variable('AWS_PRELOAD_METADATA', True)
    
    AWS_STATIC_S3_BUCKET = get_project_env_variable('AWS_STATIC_S3_BUCKET',None)
    AWS_STATIC_S3_DOMAIN = get_aws_domain('static', AWS_STATIC_S3_BUCKET, None)
    
    AWS_STATIC_URL_PROTOCOL = get_project_env_variable('AWS_STATIC_URL_PROTOCOL','http:')
    
    if AWS_STATIC_S3_BUCKET:
        STATIC_ROOT = AWS_STATIC_S3_BUCKET
        STATICFILES_STORAGE = 'django_setup.aws_s3.backends.StaticS3Storage'
        STATIC_URL = '%s/' % AWS_STATIC_S3_DOMAIN
    else:
        # URL prefix for static files.
        # For local development, we use the default
        STATIC_URL = '/static/'
        STATIC_ROOT = 'static/'
        STATICFILES_STORAGE = global_settings.STATICFILES_STORAGE
    return STATIC_URL, STATIC_ROOT, STATICFILES_STORAGE, \
            AWS_PRELOAD_METADATA, AWS_STATIC_S3_BUCKET, \
            AWS_STATIC_S3_DOMAIN, AWS_STATIC_URL_PROTOCOL

def get_media_settings():
    AWS_MEDIA_S3_BUCKET = get_project_env_variable('AWS_MEDIA_S3_BUCKET',None)
    AWS_MEDIA_S3_DOMAIN = get_aws_domain('media', AWS_MEDIA_S3_BUCKET)
    
    AWS_MEDIA_URL_PROTOCOL = get_project_env_variable('AWS_MEDIA_URL_PROTOCOL','http')
    
    if AWS_MEDIA_S3_BUCKET:
        MEDIA_ROOT = AWS_MEDIA_S3_BUCKET
        DEFAULT_FILE_STORAGE = 'django_setup.aws_s3.backends.MediaS3Storage'
        MEDIA_URL = '%s/' % AWS_MEDIA_S3_DOMAIN
    else:
        # URL prefix for static files.
        # For local development, we use the default
        MEDIA_URL = '/media/'
        DEFAULT_FILE_STORAGE = global_settings.DEFAULT_FILE_STORAGE
        # Absolute filesystem path to the directory that will hold user-uploaded files.
        # Example: "/home/media/media.lawrence.com/media/"
        MEDIA_ROOT = 'media/'
    
    return MEDIA_URL, MEDIA_ROOT, DEFAULT_FILE_STORAGE,\
           AWS_MEDIA_S3_BUCKET, AWS_MEDIA_S3_DOMAIN, \
           AWS_MEDIA_URL_PROTOCOL
