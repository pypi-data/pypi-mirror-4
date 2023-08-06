from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from zope.interface import implements

try:
    from plone.app.blob.field import FileField as MediaFileField
except:
    from Products.Archetypes.atapi import FileField as MediaFileField

try:
    from Products.LinguaPlone.public import *
except ImportError:
    from Products.Archetypes.atapi import *

from Products.Archetypes.atapi import DisplayList

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.newsitem import ATNewsItem, ATNewsItemSchema

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.validation import V_REQUIRED

from operun.media.interfaces import IMedia
from operun.media.config import PROJECTNAME

from operun.media import MediaMessageFactory as _

SELECTION = DisplayList((
    ('internal', 'Hochgeladene Datei'),
    ('external', 'Verlinkte Datei'),
    ))


MediaSchema = ATNewsItemSchema.copy()
MediaSchema['text'].primary = False

MediaSchema = MediaSchema + Schema((

    BooleanField('showimage',
        storage = AnnotationStorage(),
        widget = BooleanWidget(label=_(u"Show Image"),
                            description=_(u"Display the Image beside the Body Text."),
                            ),
        ),     

    StringField('link',
        searchable = False,
        required = False,
        languageIndependent = True,
        storage = AnnotationStorage(),
        widget = StringWidget(label = _(u"Link"),
                              description = _(u"Please enter the URL to a file or YouTube video."),
                              ),     
        ),
        
    MediaFileField('file',
        primary= True,
        searchable = False,
        required = False,
        languageIndependent = True,
        storage = AnnotationStorage(),
        validators = (('isNonEmptyFile', V_REQUIRED), ('isFileType', V_REQUIRED), ('checkFileMaxSize', V_REQUIRED),),
        widget = FileWidget(label = _(u"Flash file or music file"),
                            description = _(u"Upload a audio or video file. As Flash or mp3"),
                            ),
        ),
        
    MediaFileField('fileMP4',
        searchable = False,
        required = False,
        languageIndependent = True,
        storage = AnnotationStorage(),
        validators = (('isNonEmptyFile', V_REQUIRED), ('checkFileMaxSize', V_REQUIRED),),
        widget = FileWidget(label = _(u"MP4 File"),
                            description = _(u"Upload a audio or video file. As MP4 file"),
                            ),
        ),
        
    MediaFileField('fileOGG',
        searchable = False,
        required = False,
        languageIndependent = True,
        storage = AnnotationStorage(),
        validators = (('isNonEmptyFile', V_REQUIRED), ('checkFileMaxSize', V_REQUIRED),),
        widget = FileWidget(label = _(u"Ogg File"),
                            description = _(u"Upload a audio or video file. As Ogg file"),
                            ),
        ),

    IntegerField('width',
        searchable = False,
        required = True,
        storage = AnnotationStorage(),
        default = 425,
        widget = IntegerWidget(label=_(u"Player width"),
                            description=_(u"Enter the player width."),
                            ),     
        ),

    IntegerField('height',
        searchable = False,
        required = True,
        storage = AnnotationStorage(),
        default = 350,
        widget = IntegerWidget(label=_(u"Player height"),
                            description=_(u"Enter the player height."),
                            ),     
        ),

    BooleanField('downloadlink',
        storage = AnnotationStorage(),
        widget = BooleanWidget(label=_(u"Show download link"),
                            description=_(u"Display a link to download the file below the player."),
                            ),
        ),     

    BooleanField('audiomode',
        storage = AnnotationStorage(),
        widget = BooleanWidget(label=_(u"Audio mode"),
                            description=_(u"Check to display the palyer controls only."),
                            ),
        ),     
        
    StringField('selection',
        searchable = False,
        storage = AnnotationStorage(),
        vocabulary = SELECTION,
        widget = SelectionWidget(label=_(u"Select source"),
                            description=_(u"Please select what to display."),
                            ),     
        ),
        
    ),
)

MediaSchema['title'].storage = AnnotationStorage()
MediaSchema['description'].storage = AnnotationStorage()
MediaSchema['text'].storage = AnnotationStorage()
MediaSchema['image'].widget.description = _(u'label_image_field', default = u'Will be shown in the folder listing, and as screenshot. Image will be scaled to a sensible size.')
MediaSchema['image'].schemata = 'Media'
MediaSchema['imageCaption'].schemata = 'Media'
MediaSchema['showimage'].schemata = 'Media'
MediaSchema['downloadlink'].schemata = 'Media'
MediaSchema['audiomode'].schemata = 'Media'
MediaSchema['link'].schemata = 'Media'
MediaSchema['file'].schemata = 'Media'
MediaSchema['fileMP4'].schemata = 'Media'
MediaSchema['fileOGG'].schemata = 'Media'
MediaSchema['width'].schemata = 'Media'
MediaSchema['height'].schemata = 'Media'
MediaSchema['selection'].schemata = 'Media'

finalizeATCTSchema(MediaSchema, folderish=False, moveDiscussion=False)

class Media(ATNewsItem):
    """Media
    """

    implements(IMedia)

    portal_type = "Media"
    _at_rename_after_creation = True

    schema = MediaSchema
    schema.moveField('showimage', before = 'link')
    
    title = ATFieldProperty('title')
    description = ATFieldProperty('description')
    text = ATFieldProperty('text')
    
    showimage = ATFieldProperty('showimage')
    link = ATFieldProperty('link')
    file = ATFieldProperty('file')
    
    width = ATFieldProperty('width')
    height = ATFieldProperty('height')
    
    downloadlink = ATFieldProperty('downloadlink')
    audiomode = ATFieldProperty('audiomode')
    
    security = ClassSecurityInfo()
        
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)
    
    def __bobo_traverse__(self, REQUEST, name):

        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                return image

        if name.startswith('splash'):
            field = self.getField('image')
            image = None
            scalename = 'large'
            image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                return image
        
        if name.startswith(self.getFileName()) and self.isFile():
            field = self.getWrappedField('file')
            return field.download(self)
            
        return super(Media, self).__bobo_traverse__(REQUEST, name)


    def getFileName(self):
        """Returns the file name needed by flowplayer"""
        
        try: 
            filename = self.getFilename()
            if filename:
                return filename
            else:
                return ''

        except AttributeError:
            # fallback for ATFile 
            filename = self.file.filename
            if filename:
                return filename
            else:
                return ''

    security.declareProtected(View, 'download')
    def downloadOGG(self, REQUEST=None, RESPONSE=None):
        """Download the OGGfile
        """

        if self.isFile(codec="OGG"):
            field = self.getWrappedField('fileOGG')
            return field.download(self)
        return None

    security.declareProtected(View, 'download')
    def downloadMP4(self, REQUEST=None, RESPONSE=None):
        """Download the MP4file
        """

        if self.isFile(codec="MP4"):
            field = self.getWrappedField('fileMP4')
            return field.download(self)
        return None
 
    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the file
        """

        if self.isFile():
            field = self.getWrappedField('file')
            return field.download(self)
        return None
    
    def isFile(self, codec=""):
        """Check if there is a File"""

        size = self.getWrappedField('file' + codec).get_size(self)
        if size: return True
        return None
        
registerType(Media, PROJECTNAME)
