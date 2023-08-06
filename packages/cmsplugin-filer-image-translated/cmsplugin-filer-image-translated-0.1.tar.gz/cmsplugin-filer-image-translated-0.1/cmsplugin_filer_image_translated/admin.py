"""Admin classes for the ``filer_image_translated`` app."""
from filer import settings
from django.contrib import admin
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from simple_translation.admin import TranslationAdmin
from simple_translation.utils import get_preferred_translation_from_lang
from filer.admin.imageadmin import ImageAdmin
from filer.models import Image



class ImageAdmin(TranslationAdmin, ImageAdmin):
    """
    Custom admin for images that uses the translateable fields.

    Unfortunately we cannot use 'fields' here and must use 'exclude' because
    the translateable fields get added to the admin too late.

    """
    exclude = [
        'folder', 'name', '_file_size', 'original_filename', 'owner',
        'is_public', '_height', '_width', 'must_always_publish_author_credit',
        'must_always_publish_copyright', 'author', 'subject_location',
        'description', 'default_alt_text', 'default_caption']
    list_display = ['trans_name', 'languages', ]

    def trans_name(self, obj):
        lang = get_language()
        trans = get_preferred_translation_from_lang(obj, lang)
        return trans.trans_name
    trans_name.short_description = _('Name')


ImageAdmin.fieldsets = None

admin.site.unregister(Image)
admin.site.register(Image, ImageAdmin)
