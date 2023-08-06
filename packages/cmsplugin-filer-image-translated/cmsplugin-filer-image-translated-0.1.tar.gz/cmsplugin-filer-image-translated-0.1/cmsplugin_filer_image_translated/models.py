"""Models for the ``tagging_translated`` app."""
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from filer.models import Image


class ImageTranslation(models.Model):
    """Translateable fields for the ``tagging.Tag`` model."""
    trans_name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        blank=True,
    )

    trans_description = models.TextField(
        max_length=256,
        verbose_name=_('Description'),
        blank=True,
    )

    trans_alt_text = models.CharField(
        max_length=512,
        verbose_name=_('Alt text'),
        blank=True,
    )

    trans_caption = models.CharField(
        max_length=512,
        verbose_name=_('Caption'),
        blank=True,
    )

    # Needed by simple-translation
    image = models.ForeignKey(Image, verbose_name=_('Image'))
    language = models.CharField(max_length=2, verbose_name=_('Language'))
