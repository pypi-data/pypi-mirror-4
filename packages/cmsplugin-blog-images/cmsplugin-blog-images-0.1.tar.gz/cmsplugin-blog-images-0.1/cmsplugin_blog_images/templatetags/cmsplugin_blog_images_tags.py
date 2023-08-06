"""Templatetags for the ``cmsplugin_blog_images`` app."""
from django import template


register = template.Library()


@register.assignment_tag
def get_entry_images(entry):
    """
    Returns the images for the given entry.

    :param entry: An Entry instance.

    """
    qs = entry.images.all().order_by('position')
    return qs
