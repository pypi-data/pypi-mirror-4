"""Factories for the ``object_attachments`` app."""
import factory

from document_library.tests.factories import DocumentFactory
from object_attachments.tests.test_app.models import DummyModel


from ..models import ObjectAttachment


class DummyModelFactory(factory.Factory):
    """Factory for the ``DummyModel`` model."""
    FACTORY_FOR = DummyModel


class ObjectAttachmentFactory(factory.Factory):
    """Factory for the ``EntryAttachment`` model."""
    FACTORY_FOR = ObjectAttachment

    content_object = factory.SubFactory(DummyModelFactory)
    document = factory.SubFactory(DocumentFactory)
