from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from callback.managers import CallbackMapManager


class CallbackMap(models.Model):
    hash_id = models.CharField(max_length=40)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    is_active = models.BooleanField(default=True)

    is_error = models.BooleanField(default=False)
    error_msg = models.TextField(blank=True)

    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(default=timezone.now)

    objects = CallbackMapManager()

    # Methods
    def __unicode__(self):
        return self.hash_id

    def mark_complete(self):
        self.is_active = False
        self.is_error = False
        self.save()

    def mark_error(self, msg):
        self.is_active = False
        self.is_error = True
        self.error_msg = msg
        self.save()

    def mark_active(self):
        self.is_active = True
        self.is_error = False
        self.save()

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_on = timezone.now()
        super(CallbackMap, self).save(*args, **kwargs)
