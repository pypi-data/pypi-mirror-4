from django.conf import settings


class CallbackException(Exception):
    pass


class CallbackBase(object):
    def process(self, model_instance):
        raise CallbackException('Not Implemented')
