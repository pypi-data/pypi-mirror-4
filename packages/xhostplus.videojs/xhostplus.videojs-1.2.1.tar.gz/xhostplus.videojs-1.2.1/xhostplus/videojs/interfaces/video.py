from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from xhostplus.videojs import videojsMessageFactory as _

class IVideo(Interface):
    """A video type"""
    
    # -*- schema definition goes here -*-
