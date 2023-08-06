from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella_attachments.views import download_attachment

urlpatterns = patterns('',
    url(r'^%s/(?P<slug>.*)' % slugify(_('download')), download_attachment, name='ella_attachments-download'),
)
