"""Models for the ``object_attachments`` app."""
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ObjectAttachment(models.Model):
    """
    Mapping class to map any object to ``Document`` objects.

    """
    document = models.ForeignKey(
        'document_library.Document',
        verbose_name=_('Document'),
    )

    position = models.PositiveIntegerField(
        verbose_name=_('Position'),
        null=True, blank=True,
    )

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['position', ]
