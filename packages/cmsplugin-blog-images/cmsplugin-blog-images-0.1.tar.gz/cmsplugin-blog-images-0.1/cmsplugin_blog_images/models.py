"""Models for the ``cmsplugin_blog_categories`` app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from filer.fields.file import FilerFileField


class EntryImage(models.Model):
    """
    A blog ``Entry`` can have one or more images.

    This enables you to upload a dedicated header image for your blog post
    or even more of them to be shown in a slider.

    """
    entry = models.ForeignKey(
        'cmsplugin_blog.Entry',
        verbose_name=_('Entry'),
        related_name='images',
    )

    image = FilerFileField(
        verbose_name=_('Image'),
        null=True, blank=True,
    )

    copyright_notice = models.CharField(
        max_length=1024,
        verbose_name=_('Copyright notice'),
        blank=True,
    )

    position = models.PositiveIntegerField(
        verbose_name=_('Position'),
        null=True, blank=True,
    )
