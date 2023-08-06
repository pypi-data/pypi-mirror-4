"""Admin classes for the ``object_attachments`` app."""
from django.contrib.contenttypes.generic import GenericTabularInline

from .models import ObjectAttachment


class ObjectAttachmentInline(GenericTabularInline):
    model = ObjectAttachment
    extra = 1
    raw_id_fields = ['document', ]
