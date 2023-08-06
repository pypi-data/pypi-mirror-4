from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize
from operun.media.interfaces import IMedia

try: 
    # Plone 4 and higher 
    import plone.app.blob 
    BLOB_SUPPORT = True 
except ImportError: 
    BLOB_SUPPORT = False

class MediaView(BrowserView):

    template = ViewPageTemplateFile('media.pt')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.success = True
        self.link = self.context.getLink()
        self.selection = self.context.getSelection()
        
    def __call__(self):
        context = aq_inner(self.context)
        return self.template()
    
    def isYouTube(self):
        """Check if there is a youtube url and external source is selected to play"""
        if 'youtube' in self.link.split('.'):
            return True
        return None
    
    def isMediaPlayer(self):
        """Check if there is a file uploaded and internal source is selected to play"""
        if self.context.isFile():
            return True
        return None
    
    def getPlayer(self):
        """Return wich player to display"""
        
        youtube = self.isYouTube()
        player = self.isMediaPlayer()
        
        if youtube and player:
            if self.selection:
                return self.selection
            else:
                return 'external'
        elif youtube or player:
            if not self.isYouTube():
                return 'internal'
            if not self.isMediaPlayer():
                return 'external'
        else:
            return None
    
    def getYouTubeLink(self):
        """ Returns the URL used by the embed code by YouTube
        """
        
        return self.link.replace('watch?v=', 'v/')
 
    def getMP4DownloadLink(self):
        """ Returns a download link
        """
        context = aq_inner(self.context)
        extension = '?e=.mp4'
        return context.absolute_url() + '/downloadMP4' + extension
  
    def getOGGDownloadLink(self):
        """ Returns a download link
        """
        context = aq_inner(self.context)
        extension = '?e=.ogv'
        return context.absolute_url() + '/downloadOGG' + extension
   
    def getDownloadLink(self):
        """ Returns a download link
        """
        context = aq_inner(self.context)
        type = context.file.getContentType()
        extension = ''
        
        if BLOB_SUPPORT:
            if hasattr(context.file, 'getBlob'):
                # return a view that return the aquisition-wrapped object 
                if type.startswith('audio/'):
                    extension = '?e=.mp3'
                return context.absolute_url() + '/download' + extension
                
            # Fallback for media-files added before blob-support in operun.media.
            # context.file.absolute_url() doesn't return file-extensions, so we do some guessing.   
            else:
                if type.startswith('audio/'):
                    extension = '?e=.mp3'
                if type.startswith('video/'):
                    extension = '?e=.flv'
                return context.file.absolute_url() + extension 

        else:
            # get the file without plone.app.blob   
            return context.absolute_url() + '/' + context.getFileName()

    def getPlayerWidth(self):
        """ Returns the width of the media player
        """
        
        context = aq_inner(self.context)
        
        return context.getWidth()

    
    def getPlayerHeight(self):
        """ Returns the height of the media player
        """
        
        context = aq_inner(self.context)
        
        if context.getAudiomode():
            return 24
        else:
            return context.getHeight() + 24
