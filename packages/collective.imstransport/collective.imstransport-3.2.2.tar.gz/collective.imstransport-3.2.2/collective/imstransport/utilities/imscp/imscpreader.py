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
from collective.imstransport.utilities.imscp.cpreader import CPReader
from zope.component import getUtility
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from xml.parsers.expat import ExpatError
from collective.imstransport.IMS_exceptions import ManifestError
from zipfile import BadZipfile

class IMSCPReader(IMSReader):
    """ Create objects from IMS manifest. """

    def readPackage(self, file, context):
        """ Read the manifest """
        try:
            source = ZipfileReader(file)
        except BadZipfile:
             raise ManifestError, 'Internal error. No source object specified'
        objDict = {}
        cpreader = CPReader()
        manifest = source.readManifest()
        if not manifest:
            raise ManifestError, 'Could not locate manifest file "imsmanifest.xml" in the zip archive.'
        try:
            doc = cpreader.parseManifest(manifest)
        except ExpatError, e:
            raise ManifestError, str(e)
        objDict['package'] = cpreader.readPackageMetadata(doc)
        orgs = cpreader.readOrganizations(doc)
        resources = cpreader.readResources(doc)

        for x in resources:
            resid, restype, reshref = cpreader.readResourceAttributes(x)
            metadata = cpreader.readMetadata(x)
            files = cpreader.readFiles(x)

            # If the type is a file
            if restype == 'webcontent':
                if not files and reshref:
                    files = [reshref,]
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
                    objDict[hash]['id'] = id
                    if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                        objDict[hash]['title'] = id
                    objDict[hash]['path'] = self.createPathFromFile(y)

        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)
