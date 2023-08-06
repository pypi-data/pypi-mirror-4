from Products.Archetypes.atapi import DisplayList

PROJECTNAME = "operun.media"

ADD_PERMISSIONS = {
    "Media" : "operun.media: Add Media",
 }

FILES = [
    'flv',
    'f4v',
    'mp3',
] 

TYPES = [
    'application/octet-stream',
    'video/x-flv',
    'video/mp4',
    'video/x-m4v',
    'audio/mp4a-latm',
    'video/3gpp',
    'video/quicktime',
    'audio/mp4',
    'audio/mpeg'
]
