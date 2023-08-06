from storages.backends.s3boto import S3BotoStorage
from django.conf import settings

class StaticS3Storage(S3BotoStorage):
    
    def __init__(self, bucket=getattr(settings, 'AWS_STATIC_S3_BUCKET'),
                 custom_domain=getattr(settings, 'AWS_STATIC_S3_DOMAIN'),
                 secure_urls=getattr(settings, 'AWS_STATIC_S3_SECURE'),
                 url_protocol=getattr(settings, 'AWS_STATIC_URL_PROTOCOL')):
        S3BotoStorage.__init__(self, bucket=bucket,
                               custom_domain=custom_domain,
                               secure_urls=secure_urls,
                               url_protocol=url_protocol)
        
class MediaS3Storage(S3BotoStorage):
    
    def __init__(self, bucket=getattr(settings, 'AWS_MEDIA_S3_BUCKET'),
                 custom_domain=getattr(settings, 'AWS_MEDIA_S3_DOMAIN'),
                 secure_urls=getattr(settings, 'AWS_MEDIA_S3_SECURE'),
                 url_protocol=getattr(settings, 'AWS_MEDIA_URL_PROTOCOL')):
        S3BotoStorage.__init__(self, bucket=bucket,
                               custom_domain=custom_domain,
                               secure_urls=secure_urls,
                               url_protocol=url_protocol)
