"""Tests for the models of the ``cmsplugin_blog_authors`` app."""
from django.test import TestCase

from .factories import EntryAuthorFactory


class EntryAuthorTestCase(TestCase):
    """Tests for the ``EntryAuthor`` model."""
    longMessage = True

    def test_model(self):
        obj = EntryAuthorFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))
