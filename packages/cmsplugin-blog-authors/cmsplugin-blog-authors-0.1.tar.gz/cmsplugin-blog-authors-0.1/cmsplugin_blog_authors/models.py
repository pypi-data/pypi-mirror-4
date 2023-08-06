"""Models for the ``cmsplugin_blog_authors`` app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _


class EntryAuthor(models.Model):
    """
    Mapping class to map ``Entry`` objects to ``Person`` objects.

    """
    entry = models.ForeignKey(
        'cmsplugin_blog.Entry',
        verbose_name=_('Entry'),
        related_name='authors',
    )

    author = models.ForeignKey(
        'people.Person',
        verbose_name=_('Author'),
        related_name='entries',
    )

    position = models.PositiveIntegerField(
        verbose_name=_('Position'),
        null=True, blank=True,
    )

    class Meta:
        ordering = ['position', ]
