"""Admin classes for the ``cmsplugin_blog_authors`` app."""
from django.contrib import admin

from cmsplugin_blog.admin import EntryAdmin

from .models import EntryAuthor


class EntryAuthorInline(admin.TabularInline):
    model = EntryAuthor
    extra = 1
    raw_id_fields = ['author', ]


EntryAdmin.inlines = EntryAdmin.inlines[:] + [EntryAuthorInline]
