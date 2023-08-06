"""Admin classes for the ``cmsplugin_blog_categories`` app."""
from django.contrib import admin

from cmsplugin_blog.admin import EntryAdmin

from .models import EntryImage


class EntryImageInline(admin.TabularInline):
    model = EntryImage
    extra = 1


EntryAdmin.inlines = EntryAdmin.inlines[:] + [EntryImageInline]
