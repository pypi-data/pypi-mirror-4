"""Tests for the models of the ``object_attachments`` app."""
from django.test import TestCase

from .factories import ObjectAttachmentFactory


class EntryAttachmentTestCase(TestCase):
    """Tests for the ``EntryAttachment`` model."""
    longMessage = True

    def test_model(self):
        obj = ObjectAttachmentFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))
