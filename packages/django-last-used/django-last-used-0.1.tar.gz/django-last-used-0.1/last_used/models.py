
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class LastUsed(models.Model):
    user = models.ForeignKey(User)
    last_used = models.DateTimeField(default=timezone.now)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    key = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ("-last_used",)

    def __unicode__(self):
        if self.key:
            return u"%s used %s (%s) on %s" % \
                    (self.user, self.content_object, self.key, self.last_used)
        return u"%s used %s on %s" % \
                    (self.user, self.content_object, self.last_used)
