"""Factories for the ``cmsplugin_blog_authors`` app."""
import factory

from people.tests.factories import PersonFactory
from cmsplugin_blog.models import Entry

from ..models import EntryAuthor


class EntryFactory(factory.Factory):
    """Factory for the ``Entry`` model."""
    FACTORY_FOR = Entry


class EntryAuthorFactory(factory.Factory):
    """Factory for the ``EntryAuthor`` model."""
    FACTORY_FOR = EntryAuthor

    entry = factory.SubFactory(EntryFactory)
    author = factory.SubFactory(PersonFactory)
