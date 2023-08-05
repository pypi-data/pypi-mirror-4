from django.db import models
from models import CallbackMap
from base import CallbackException, CallbackBase
from signals import stored_callback, processed_callback, error_callback

REQUIRED_METHODS = ('process',)


class CallbackManager(object):
    def __init__(self):
        self._callbacks = {}

    def validate_methods(self, cls):
        for method in REQUIRED_METHODS:
            if not hasattr(cls, method):
                raise CallbackException(
                    'Cannot register class - does not contain '
                    '%s method' % method
                )

    def register_callback(self, dest_model, dest_cls):
        if not issubclass(dest_model, models.Model):
            raise CallbackException(
                'Cannot register model - not a '
                'subclass of django.db.models.Model'
            )
        if not issubclass(dest_cls, CallbackBase):
            raise CallbackException(
                'Cannot register class - not a subclass of '
                'callback.CallbackBase'
            )

        self.validate_methods(dest_cls)
        self._callbacks[dest_model] = dest_cls

    def unregister_callback(self, dest_model):
        self._callbacks.pop(dest_model, None)

    def get_callback_class(self, dest_model):
        for model, cls in self._callbacks.items():
            if isinstance(dest_model, model):
                return cls()
        raise CallbackException('Model class is not registered.')

    def store_callback(self, model_instance):
        if not model_instance.pk:
            model_instance.save()

        cls = self.get_callback_class(model_instance)
        callback_instance = CallbackMap.objects.store_callback(model_instance)
        stored_callback.send(
            sender=self,
            callback_instance=callback_instance,
            model_instance=model_instance,
        )
        return callback_instance

    def process_callback(self, callback_instance):
        model = callback_instance.content_object
        cls = self.get_callback_class(model)
        try:
            cls.process(model)
            callback_instance.mark_complete()
            processed_callback.send(
                sender=self,
                callback_instance=callback_instance,
                model_instance=model,
            )
        except Exception, e:
            callback_instance.mark_error(str(e))
            error_callback.send(
                sender=self,
                callback_instance=callback_instance,
                model_instance=model,
            )
            raise CallbackException(str(e))


callback_manager = CallbackManager()
