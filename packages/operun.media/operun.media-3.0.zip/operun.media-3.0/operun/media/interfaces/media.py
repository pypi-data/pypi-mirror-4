from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from operun.media import MediaMessageFactory as _

class IMedia(Interface):
    """Media"""

    title = schema.TextLine(title=_(u"Title"),
                                    required = True)
    
    description = schema.Text(title=_(u"Description"),
                                    description=_(u"Plain Description of the Body Text"))
    
    text = schema.Text(title=_(u"Body Text"),
                                    required = False)
    
    showimage = schema.Bool(title=_(u"Show Image"),
                                    description=_(u"Display the Image beside the Body Text."),
                                    required = False)
    
    link = schema.Text(title=_(u"Link"),
                                    description=_(u"Please enter the URL to a file or YouTube video."),
                                    required = False)
    
    file = schema.Text(title=_(u"File"),
                                    description=_(u"Upload a audio or video file."),
                                    required = False)
    
    width = schema.Int(title=_(u"Player width"),
                                    description=_(u"Enter the player width."),
                                    required = True)
    
    height = schema.Int(title=_(u"Player height"),
                                    description=_(u"Enter the player height."),
                                    required = True)

    downloadlink = schema.Bool(title=_(u"Show download link"),
                                    description=_(u"Display a link to download the file below the player."),
                                    required = False)

    audiomode = schema.Bool(title=_(u"Audio mode"),
                                    description=_(u"Check to display the palyer controls only."),
                                    required = False)