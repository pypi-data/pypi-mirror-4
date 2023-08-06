"""Registering translated models for the ``tagging_translated`` app."""
from simple_translation.translation_pool import translation_pool

from tagging.models import Tag

from .models import TagTitle


translation_pool.register_translation(Tag, TagTitle)
