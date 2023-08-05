from Products.validation.interfaces.IValidator import IValidator

from Products.ContentTypeValidator import ContentTypeValidatorMessage as _
from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from zope.i18n import translate

try:  # Plone 4 and highwer
    import plone.app.upgrade
    USE_BBB_VALIDATORS = False
except ImportError:  # BBB Plone 3
    USE_BBB_VALIDATORS = True


class ContentTypeValidator:
    """Validates a file to be of one of the given content-types
    """
    if USE_BBB_VALIDATORS:
        __implements__ = (IValidator,)
    else:
        implements(IValidator)
    name = 'ContentTypeValidator'

    def __init__(self, content_types):
        self.content_types = content_types

    def __call__(self, value, *args, **kw):
        error = translate(_('contenttype_error',
                            default=u"File has to be of one of the following content-types '${types}'",
                            mapping={'types': ', '.join(self.content_types)}), context=kw['instance'].REQUEST)
        if value and not value == 'DELETE_FILE':
            try:
                if kw['REQUEST'].form.get('%s_delete' % kw['field'].getName(), None) == 'delete':
                    return 1
                if kw['REQUEST'].form.get('%s_delete' % kw['field'].getName(), None) == 'nochange':
                    type = kw['field'].getContentType(kw['instance'])
                else:
                    mimetypes = getToolByName(kw['instance'], 'mimetypes_registry')
                    type = mimetypes.lookupExtension(value.filename.lower())
                    if type is None:
                        type = mimetypes.globFilename(value.filename)
                    try:
                        type = type.mimetypes[0]
                    except:  # wasn't able to parse mimetype
                        type = None
                if not type in self.content_types:
                    return error
            except:
                return error
        return 1
