from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ella import newman
from ella.core.models import Publishable

from ella_attachments.models import Attachment, Type

GUESS_MIMETYPE = getattr(settings, 'ATTACHMENTS_GUESS_MIMETYPE', True)

class AttachmentInlineAdmin(newman.NewmanTabularInline):
    model = Attachment.publishables.through
    extra = 3
    suggest_fields = {'attachment': ('name',)}

    verbose_name = _('Attachment')
    verbose_name_plural = _('Attachments')


class AttachmentAdmin(newman.NewmanModelAdmin):
    if GUESS_MIMETYPE:
        list_display = ('name', 'created',)
    else:
        list_display = ('name', 'type', 'created',)
    list_filter = ('type',)
    prepopulated_fields = {'slug' : ('name',)}
    rich_text_fields = {'small': ('description',)}
    raw_id_fields = ('photo',)
    suggest_fields = {'publishables': ('__unicode__', 'title', 'slug',),}


class TypeAdmin(newman.NewmanModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


def append_inlines():
    publishables = ['%s.%s' % (x._meta.app_label, x._meta.object_name)
                    for x in models.get_models() if issubclass(x, Publishable)]
    newman.site.append_inline(publishables, AttachmentInlineAdmin)


newman.site.register(Attachment, AttachmentAdmin)
newman.site.register(Type, TypeAdmin)

append_inlines()
