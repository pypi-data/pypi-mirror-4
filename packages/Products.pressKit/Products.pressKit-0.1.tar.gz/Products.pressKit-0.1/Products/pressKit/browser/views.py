import time
import string
from zope.component import getUtility
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class PressKitView(BrowserView):
    """
    Generates and returns a zip file with the contents of the press kit
    """
        
        