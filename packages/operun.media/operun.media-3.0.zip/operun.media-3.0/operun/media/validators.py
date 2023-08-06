from zope.interface import implements

from Products.validation import validation
from Products.validation.interfaces import ivalidator
from Products.validation.interfaces.IValidator import IValidator

from operun.media.config import TYPES
from operun.media.config import FILES

try:
    # Plone 4 and higher
    import plone.app.upgrade
    USE_BBB_VALIDATORS = False
except ImportError:
    # BBB Plone 3
    USE_BBB_VALIDATORS = True


class FileTypeValidator:
    """ validate files on mime type
    """

    if USE_BBB_VALIDATORS:
        __implements__ = (ivalidator,)
    else:
        implements(IValidator)
    
    def __init__(self, name):
        self.name = name
        
    def __call__(self, value, *args, **kwargs):
        
        instance = kwargs.get('instance', None)
        field = kwargs.get('field', None)
        
        if value.headers['content-type'] in TYPES and value.filename[-3:] in FILES:
            return 1
        else:
            return """ Validation failed. Content type is not supported. """