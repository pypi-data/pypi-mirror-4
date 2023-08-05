##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved.
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

from collective.imstransport.utilities.imsinterchange import IMSReader
from collective.imstransport.utilities.packagingio import ZipfileReader
from collective.imstransport.utilities.webctvista.webctvistareader import WebCTVistaReader
from zope.component import getUtility
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from xml.parsers.expat import ExpatError
from collective.imstransport.IMS_exceptions import ManifestError
from zipfile import BadZipfile

class IMSWebCTVistaReader(IMSReader):
    """ Create objects from IMS manifest. """

    def readPackage(self, file, context):
        """ Read the package """
        try:
            source = ZipfileReader(file)
        except BadZipfile:
             raise ManifestError, 'Internal error. No source object specified'
        self.readPackageFile(source, context, manifestfile='imsmanifest.xml')

    def readPackageFile(self, source, context, manifestfile, pagedata=None):
        """ Read the manifest """
        objDict = {}
        webctvistareader = WebCTVistaReader()
        manifest = source.readManifest(manifestfile=manifestfile)
        if not manifest:
            raise ManifestError, 'Could not locate manifest file "%s" in the zip archive.' %manifestfile
        try:
            doc = webctvistareader.parseManifest(manifest)
        except ExpatError, e:
            raise ManifestError, str(e)

        manifestmetadata = webctvistareader.readMetadata(doc)
        # if the manifest is a learning module
        if manifestmetadata.has_key('webcttype') and manifestmetadata['webcttype'] == 'webct.learningModule':
            objDict['package'] = manifestmetadata

        orgs = webctvistareader.readOrganizations(doc)
        resources = webctvistareader.readResources(doc)

        for x in resources:
            resid, restype, reshref = webctvistareader.readResourceAttributes(x)
            files = webctvistareader.readFiles(x)
            # If the manifest is a page
            if restype == 'webct.manifest':
                for y in files:
                    if orgs.has_key(resid) and manifestmetadata['webcttype'] == 'webct.page':
                        self.readPackageFile(source, context, files[0], manifestmetadata)
                    else:
                        self.readPackageFile(source, context, files[0])
            # If the manifest is a file
            elif restype == 'webcontent' and manifestmetadata['webcttype'] == 'webct.file':
                hash = resid
                objDict[hash] = manifestmetadata
                webctvistareader.readContentMetadata(doc, objDict[hash])
                if pagedata:
                    objDict[hash]['title'] = pagedata['title']
                    objDict[hash]['excludeFromNav'] = False
                else:
                    objDict[hash]['excludeFromNav'] = True
                objDict[hash]['file'] = files[0]
                objDict[hash]['type'] = self.determineType(objDict[hash], objDict[hash]['id'])

        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)


