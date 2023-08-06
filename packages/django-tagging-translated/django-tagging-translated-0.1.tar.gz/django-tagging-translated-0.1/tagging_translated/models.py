"""Models for the ``tagging_translated`` app."""
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag


class TagTitle(models.Model):
    """Translateable fields for the ``tagging.Tag`` model."""
    trans_name = models.CharField(
        max_length=256,
        verbose_name=_('Name in current language'),
    )

    # Needed by simple-translation
    tag = models.ForeignKey(Tag, verbose_name=_('Tag'))
    language = models.CharField(max_length=2, verbose_name=_('Language'))


@receiver(post_save, sender=Tag)
def tag_post_save_handler(sender, **kwargs):
    """
    Makes sure that a translation is created when a tag is saved.

    Also ensures that the original tag name gets updated when the english
    translation is updated.

    TODO: This will create two tags when a tag is saved through the admin

    """
    instance = kwargs.get('instance')
    try:
        translation = instance.tagtitle_set.get(language='en')
    except TagTitle.DoesNotExist:
        translation = TagTitle.objects.create(trans_name=instance.name,
            tag=instance, language='en')
    if translation.trans_name != instance.name:
        instance.name = translation.trans_name
        instance.save_base(raw=True)
