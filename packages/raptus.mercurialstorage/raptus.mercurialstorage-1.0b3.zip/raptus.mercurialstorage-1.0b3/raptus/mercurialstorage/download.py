import os

from zope.annotation import IAnnotations

from Products.Five.browser import BrowserView
from Products.Archetypes.utils import contentDispositionHeader

# Import conditionally, so we don't introduce a hard dependency
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
    FILE_NORMALIZER = True
except ImportError:
    FILE_NORMALIZER = False

class Download(BrowserView):
    """ View to download a specific file
    """
    
    def __call__(self, name, rev=False):
        field = self.context.getField(name)
        if not rev:
            return field.download(self.context)
        
        storage = field.getStorage(self.context)
        info = storage.getInfoByRevision(self.context, name, rev)
        if not info:
            return field.download(self.context)
        contents = storage.getByRevision(self.context, name, rev)
        
        filename = field.getFilename(self.context)
        if not filename:
            filename = os.path.basename(info['filepath'])
        kwargs = {'filename': filename,
                  'mimetype': info['mimetype']}
        file = field._wrapValue(self.context, contents, **kwargs)
        if filename is not None:
            if FILE_NORMALIZER:
                filename = IUserPreferredFileNameNormalizer(self.request).normalize(
                    unicode(filename, self.context.getCharset()))
            else:
                filename = unicode(filename, self.context.getCharset())
            header_value = contentDispositionHeader(
                disposition='attachment',
                filename=filename)
            self.request.RESPONSE.setHeader("Content-Disposition", header_value)
        return file.index_html(self.request, self.request.RESPONSE)
        