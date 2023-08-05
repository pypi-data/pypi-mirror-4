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

from zope.interface import implements
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from zope.component import getUtility
from collective.imstransport.utilities.imsinterchange import IMSReader
from collective.imstransport.utilities.packagingio import ZipfileReader
from collective.imstransport.utilities.imscc.ccreader import CCReader
from collective.imstransport import IMSTransportMessageFactory as _
from xml.parsers.expat import ExpatError
from collective.imstransport.IMS_exceptions import ManifestError
from zipfile import BadZipfile

class IMSCCReader(IMSReader):
    """ Create objects from IMS manifest. """

    def readPackage(self, file, context):
        """ Read the manifest """
        try:
            source = ZipfileReader(file)
        except BadZipfile:
             raise ManifestError, 'Internal error. No source object specified'
        objDict = {}
        ccreader = CCReader()
        manifest = source.readManifest()
        if not manifest:
            raise ManifestError, 'Could not locate manifest file "imsmanifest.xml" in the zip archive.'
        try:
            doc = ccreader.parseManifest(manifest)
        except ExpatError, e:
            raise ManifestError, str(e)
        objDict['package'] = {}
        ccreader.readPackageMetadata(doc, objDict['package'])
        orgs = ccreader.readOrganizations(doc)
        resources = ccreader.readResources(doc)

        for x in resources:
            resid, restype, reshref = ccreader.readResourceAttributes(x)
            metadata = ccreader.readMetadata(x)
            files = ccreader.readFiles(x)
            # If the type is a link
            if restype == 'imswl_xmlv1p0':
                for y in files:
                    hash = resid + y
                    objDict[hash] = metadata
                    id = self.createIdFromFile(y)
                    objDict[hash]['id'] = id.replace('.xml','')
                    objDict[hash]['path'] = self.createPathFromFile(y)
                    linkfile = source.readFile(y)
                    title, location = ccreader.getLinkInfo(linkfile)
                    objDict[hash]['type'] = 'Link'
                    objDict[hash]['title'] = title
                    objDict[hash]['remoteUrl'] = location
            # If the type is a file
            elif restype == 'webcontent':
                for y in files:
                    hash = resid + y
                    # If there is only one file, or it matches the reshref
                    # add the metadata to it if it exists
                    if y == reshref or len(files) == 1:
                        objDict[hash] = metadata
                        # If it is listed in the org section
                        if orgs.has_key(resid):
                            objDict[hash]['position'] = orgs[resid][0]
                            objDict[hash]['excludeFromNav'] = False
                            # Use 'and' as opposed to 'or' to avoid KeyError
                            if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                                objDict[hash]['title'] = orgs[resid][1]
                        else:
                            objDict[hash]['excludeFromNav'] = True
                        objDict[hash]['file'] = y
                        objDict[hash]['type'] = self.determineType(objDict[hash], y)
                    # If it is just a lowly file
                    else:
                        objDict[hash] = {}
                        objDict[hash]['excludeFromNav'] = True
                        objDict[hash]['file'] = y
                        objDict[hash]['type'] = self.determineType(objDict[hash], y)
                    # Add to all files
                    id = self.createIdFromFile(y)
                    if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                        objDict[hash]['title'] = id
                    objDict[hash]['id'] = id
                    objDict[hash]['path'] = self.createPathFromFile(y) 

        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)

        







