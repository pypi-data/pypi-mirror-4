import time
import string
import os
from zope.component import getUtility
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
import zipfile
import urllib

class DownloadZipView(BrowserView):
    def generate_zip(self):
        """
        Generates and returns a zip file with the contents of the press kit
        """
        #Get all the files and images on the presskit
        catalog = getToolByName(self.context, 'portal_catalog')
        files = catalog.searchResults(path = {'query' : '/'.join(self.context.getPhysicalPath()),
            'depth' : 1 },
            sort_on = 'getObjPositionInParent',
        ) 
        
        mimetype = 'application/zip'
        zipfilename="/var/tmp/%s.zip"%self.context.id
        
        archive = zipfile.ZipFile(zipfilename,"a")
        for f in files:
            obj = f.getObject()
            fileobject = obj.getFile().getBlob().open()
            filename = obj.id
            archive.writestr(filename, fileobject.read())
            
        archive.close()
        
        archivefile = open(zipfilename, "r")
        
        archiveraw = archivefile.read()
        archivefile.close()
        os.remove(zipfilename)
        
        self.request.response.setHeader('content-type', mimetype)
        self.request.response.setHeader('content-length', len(archiveraw))
        self.request.response.setHeader('Content-Disposition',
            ' attachment; filename=%s' % (urllib.quote(zipfilename.split("/")[-1:][0])))

        self.request.response.write(archiveraw)
        
        