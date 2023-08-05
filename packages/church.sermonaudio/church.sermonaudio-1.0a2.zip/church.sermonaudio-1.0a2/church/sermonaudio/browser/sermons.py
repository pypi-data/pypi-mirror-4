# -*- coding: utf-8 -*-
"""A Folder view that lists Todo Items."""

from Acquisition import aq_inner
from five import grok
from Products.ATContentTypes.interface import IATFolder

import time

# Search for templates in the current directory.
# Hopefully this line won't be needed in the future as I hope that we can tell
# grok to look in the current dir by default.
grok.templatedir('.')


class Sermons(grok.View):
    """A BrowserView to display a Sermon listing on a Folder."""
    # we use the name Sermons, by convention grok will look for
    # a corresponding template called sermons.pt
    grok.context(IATFolder)  # type of object on which this View is available
    grok.require('zope2.View')  # what permission is needed for access
    
    def timestamp(self):
        return time.time()
    
    def hello(self):
        context = self.context.aq_inner
        contents = context.folderlistingFolderContents()
        return [item.date.strftime('%b %d, %Y') for item in contents]
        

