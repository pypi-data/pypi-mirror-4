"""Registering translated models for the ``filer_image_translated`` app."""
from simple_translation.translation_pool import translation_pool

from filer.models import Image

from .models import ImageTranslation


translation_pool.register_translation(Image, ImageTranslation)
