"""Admin classes for the ``tagging_translated`` app."""
from django.contrib import admin
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from simple_translation.admin import TranslationAdmin
from simple_translation.utils import get_preferred_translation_from_lang
from tagging.admin import TagAdmin
from tagging.models import Tag



class TagAdmin(TranslationAdmin, TagAdmin):
    exclude = ['name', ]
    list_display = ['trans_name', 'languages', ]

    def trans_name(self, obj):
        lang = get_language()
        trans = get_preferred_translation_from_lang(obj, lang)
        return trans.trans_name
    trans_name.short_description = _('Name')




admin.site.unregister(Tag)
admin.site.register(Tag, TagAdmin)
