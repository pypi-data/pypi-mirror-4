import os
from datetime import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ella.core.box import Box
from ella.core.models import Publishable
from ella.photos.models import Photo


UPLOAD_TO = getattr(settings, 'ATTACHMENTS_UPLOAD_TO', 'attachments/%Y/%m/%d')


class Type(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True)
    mimetype = models.CharField(_('Mime type'), max_length=100,
            help_text=_('consult http://www.sfsu.edu/training/mimetype.htm'))

    class Meta:
        ordering = ('name',)
        verbose_name = _('Type')
        verbose_name_plural = _('Types')

    def __unicode__(self):
        return self.name


class AttachmentBox(Box):
    def get_context(self):
        "Updates box context with attachment-specific variables."
        cont = super(AttachmentBox, self).get_context()
        cont.update({
            'name' : self.params.get('name', self.obj.name),
            'description' : self.params.get('description', self.obj.description),
            'attachment' : self.params.get('attachment', self.obj.attachment),
            'type_name': self.params.get('type_name', self.obj.type.name),
            'type_mimetype': self.params.get('type_mimetype', self.obj.type.mimetype),
        })
        return cont
    
    def _get_template_list(self):    
        " Get the hierarchy of templates belonging to the object/box_type given. "
        t_list = []
        base_path = 'box/content_type/%s/' % self.opts
        
        if hasattr(self.obj, 'slug'):
            t_list.append(base_path + '%s/%s.html' % (self.obj.slug, self.box_type,))
            
        if hasattr(self.obj, 'type'):
            t_list.append(base_path + 'type/%s/%s.html' % (self.obj.type.slug, self.box_type,))
            
        t_list.append(base_path + '%s.html' % (self.box_type,))
        t_list.append(base_path + 'box.html')

        t_list.append('box/%s.html' % self.box_type)
        t_list.append('box/box.html')

        return t_list


class Attachment(models.Model):
    box_class = AttachmentBox

    name = models.CharField(_('Name'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)

    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'), related_name='photos')
    publishables = models.ManyToManyField(Publishable, blank=True, null=True,
                                          verbose_name=_('Publishables'))

    description = models.TextField(_('Description'), blank=True, null=True, default=None)

    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)

    attachment = models.FileField(_('Attachment'), upload_to=UPLOAD_TO)

    type = models.ForeignKey(Type, verbose_name=_('Attachment type'), blank=True, null=True, default=None)

    def get_download_url(self):
        return reverse('ella_attachments-download', kwargs={'slug': self.slug})

    def get_absolute_url(self):
        return self.attachment.url

    def filename(self):
        return os.path.basename(self.attachment.url)

    class Meta:
        ordering = ('created',)
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    def __unicode__(self):
        return self.name
