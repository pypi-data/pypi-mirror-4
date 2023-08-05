# -*- coding: utf-8 -*-
"""A Folder view that lists Todo Items."""

from five import grok
from Products.ATContentTypes.interface import IATFolder

# Search for templates in the current directory.
grok.templatedir('.')


class Quizzes(grok.View):
    """A BrowserView to display the Quizzes listing on a Folder."""

    grok.context(IATFolder)  # type of object on which this View is available
    grok.require('zope2.View')  # what permission is needed for access
