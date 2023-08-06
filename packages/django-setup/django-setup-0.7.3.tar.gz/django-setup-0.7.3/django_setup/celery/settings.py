# -*- coding: utf-8 -*-
import djcelery

def get_sqs_broker_url(AWS_CELERY_KEY_ID, AWS_CELERY_SECRET_KEY):
    return 'sqs://%s:%s@' % (AWS_CELERY_KEY_ID, AWS_CELERY_SECRET_KEY)

def set_celery(INSTALLED_APPS, CELERY_DEFAULT_QUEUE, BROKER_TRANSPORT='sqs',
                BROKER_TRANSPORT_OPTIONS = {}, CELERY_IGNORE_RESULT=True):
    djcelery.setup_loader()
    INSTALLED_APPS += ('djcelery', )    
    CELERY_QUEUES = {
        CELERY_DEFAULT_QUEUE: {
            'exchange': CELERY_DEFAULT_QUEUE,
            'binding_key': CELERY_DEFAULT_QUEUE,
        }
    }
    if BROKER_TRANSPORT=='sqs' and not BROKER_TRANSPORT_OPTIONS:
        BROKER_TRANSPORT_OPTIONS = {'region': 'us-east-1',}
    return INSTALLED_APPS, BROKER_TRANSPORT, BROKER_TRANSPORT_OPTIONS, CELERY_DEFAULT_QUEUE, CELERY_QUEUES, CELERY_IGNORE_RESULT
