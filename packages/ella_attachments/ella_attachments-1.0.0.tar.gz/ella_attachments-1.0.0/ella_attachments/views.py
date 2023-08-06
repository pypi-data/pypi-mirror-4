from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404


GUESS_MIMETYPE = getattr(settings, 'ATTACHMENTS_GUESS_MIMETYPE', True)

def download_attachment(request, slug):
    from ella_attachments.models import Attachment
    import mimetypes
    attachment = get_object_or_404(Attachment, slug=slug)

    # Create the HttpResponse object with the appropriate PDF headers.
    if attachment.type is None:
        mimetype = mimetypes.guess_type(attachment.attachment.url)
    else:
        mimetype = attachment.type.mimetype
    response = HttpResponse(mimetype=mimetype)
    response['Content-Disposition'] = 'attachment; filename=%s' % attachment.filename

    response.write(attachment.attachment.read())
    return response
    
