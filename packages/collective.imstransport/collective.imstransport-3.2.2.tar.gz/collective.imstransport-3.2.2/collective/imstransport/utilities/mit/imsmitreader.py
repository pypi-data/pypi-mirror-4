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
from collective.imstransport.utilities.mit.mitreader import MITReader
from zope.component import getUtility
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from xml.parsers.expat import ExpatError
from collective.imstransport.IMS_exceptions import ManifestError
from zipfile import BadZipfile

class IMSMITReader(IMSReader):
    """ Create objects from IMS manifest. """

    def readPackage(self, file, context):
        """ Read the manifest """
        try:
            source = ZipfileReader(file)
        except BadZipfile:
             raise ManifestError, 'Internal error. No source object specified'
        objDict = {}
        mitreader = MITReader()
        manifest = source.readManifest()
        if not manifest:
            raise ManifestError, 'Could not locate manifest file "imsmanifest.xml" in the zip archive.'
        try:
            doc = mitreader.parseManifest(manifest)
        except ExpatError, e:
            raise ManifestError, str(e)
        base = mitreader.readManifestBase(doc)
        objDict['package'] = mitreader.readPackageMetadata(doc)
        orgs = mitreader.readOrganizations(doc)
        resources = mitreader.readResources(doc)

        for x in resources:
            resid, restype, reshref = mitreader.readResourceAttributes(x)
            #A link to external file.
            if reshref.find('http') == 0:
                continue
            location = mitreader.readLocation(x)
            if location:
                dataxml = source.readFile('%s%s' %(base,location))
                resdata = mitreader.parseDataFile(dataxml)
                metadata = mitreader.readMetadata(resdata)
            else:
                metadata = {}
            files = mitreader.readFiles(base, x)

            if not files and reshref:
                files = ['%s%s' %(base,reshref),]
            for y in files:
                hash = resid + y
                # If there is only one file, or it matches the reshref
                # add the metadata to it if it exists
                if y == reshref or len(files) == 1:
                    objDict[hash] = metadata
                    # If it is listed in the org section
                    if orgs.has_key(resid):
                        numval, navval = orgs[resid]
                        if numval:
                            objDict[hash]['position'] = numval
                            objDict[hash]['excludeFromNav'] = False
                        else:
                            objDict[hash]['excludeFromNav'] = True
                        if navval:
                            # Use 'and' as opposed to 'or' to avoid KeyError
                            if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                                objDict[hash]['title'] = orgs[resid][1]
                    else:
                        objDict[hash]['excludeFromNav'] = True
                    objDict[hash]['type'] = self.determineType(objDict[hash], y)
                    if objDict[hash]['type'] == 'Document':
                        file = source.readFile(y)
                        if file:
                            objDict[hash]['text'] = mitreader.runFilters(file, ['stripchrome'])
                    else:
                        objDict[hash]['file'] =  y
                # If it is just a lowly file
                else:
                    objDict[hash] = {}
                    objDict[hash]['excludeFromNav'] = True
                    objDict[hash]['type'] = self.determineType(objDict[hash], y)
                    if objDict[hash]['type'] == 'Document':
                        file = source.readFile(y)
                        if file:
                            objDict[hash]['text'] = mitreader.runFilters(file, ['stripchrome'])
                    else:
                        objDict[hash]['file'] =  y

                # Add to all files
                id = self.createIdFromFile(y)
                objDict[hash]['id'] = id
                if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                    objDict[hash]['title'] = id
                objDict[hash]['path'] = self.createPathFromFile(y)
                
        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)
