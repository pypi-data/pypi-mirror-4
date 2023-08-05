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
from collective.imstransport.utilities.webct.webctreader import WebCTReader
from zope.component import getUtility
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from xml.parsers.expat import ExpatError
from collective.imstransport.IMS_exceptions import ManifestError
from zipfile import BadZipfile

class IMSWebCTReader(IMSReader):
    """ Create objects from IMS manifest. """

    def readPackage(self, file, context):
        """ Read the manifest """
        try:
            source = ZipfileReader(file)
        except BadZipfile:
             raise ManifestError, 'Internal error. No source object specified'
        objDict = {}
        webctreader = WebCTReader()
        manifest = source.readManifest()
        if not manifest:
            raise ManifestError, 'Could not locate manifest file "imsmanifest.xml" in the zip archive.'
        try:
            doc = webctreader.parseManifest(manifest)
        except ExpatError, e:
            raise ManifestError, str(e)
        manifests = webctreader.readManifests(doc)
        
        for manifest in manifests:
            orgs =[]
            manifestmetadata = webctreader.readPackageMetadata(manifest)
            if manifestmetadata.has_key('webcttype') and manifestmetadata['webcttype'] == 'Course':
                objDict['package'] = manifestmetadata
            else:
                orgs = webctreader.readOrganizations(manifest)
                resources = webctreader.readResources(manifest)
                for x in resources:
                    resid, restype, reshref = webctreader.readResourceAttributes(x)
                    files = webctreader.readFiles(x)
                    # If the type is a link
                    if manifestmetadata.has_key('webcttype') and manifestmetadata['webcttype'] == 'URL':
                        for y in files:
                            hash = resid + y
                            objDict[hash] = manifestmetadata
                            id = self.createIdFromFile(y)
                            objDict[hash]['id'] = id
                            objDict[hash]['path'] = ''
                            objDict[hash]['type'] = 'Link'
                            objDict[hash]['remoteUrl'] = y
                    elif restype == 'webcontent':
                        if not files and reshref:
                            files = [reshref,]
                        for y in files:
                            hash = resid + y
                            objDict[hash] = {}
                            # Can apply manifest metadata if single file and single resource
                            if len(resources) == 1 and len(files) == 1:
                                objDict[hash] = manifestmetadata
                            if len(files) == 1:
                                # If it is listed in the org section
                                if orgs.has_key(resid):
                                    objDict[hash]['excludeFromNav'] = False
                                    # Use 'and' as opposed to 'or' to avoid KeyError
                                    if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                                        objDict[hash]['title'] = orgs[resid]
                                else:
                                    objDict[hash]['excludeFromNav'] = True
                                objDict[hash]['file'] = y
                                objDict[hash]['type'] = self.determineType(objDict[hash], y)
                            # If it is just a lowly file
                            else:
                                objDict[hash]['excludeFromNav'] = True
                                objDict[hash]['file'] = y
                                objDict[hash]['type'] = self.determineType(objDict[hash], y)
                            # Add to all files
                            id = self.createIdFromFile(y)
                            objDict[hash]['id'] = id
                            if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                                objDict[hash]['title'] = id
                            objDict[hash]['path'] = self.createPathFromFile(y)
        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)
