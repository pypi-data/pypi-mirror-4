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

from collective.imstransport.utilities.packagingio import ZipfileReader
from collective.imstransport.utilities.imsinterchange import IMSReader
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from collective.imstransport.utilities.moodle.backupreader import BackupReader
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getUtility
from xml.parsers.expat import ExpatError
import re
from collective.imstransport.IMS_exceptions import ManifestError
from zipfile import BadZipfile

class MoodleBackupReader(IMSReader):
    """ Create objects from Moodle backup package """

    def readPackage(self, file, context):
        """ Read in the package """
        try:
            source = ZipfileReader(file)
        except BadZipfile:
             raise ManifestError, 'Internal error. No source object specified'
        objDict = {}
        backupreader = BackupReader()
        moodlexml = source.readFile('moodle.xml')
        if not moodlexml:
            raise ManifestError, 'Could not locate the "moodle.xml" file in the zip archive.'            
        main = backupreader.parseMoodleXML(moodlexml)
        mods = backupreader.readMods(main)
        visibleids = backupreader.readSections(main)
        for mod in mods:
            metadata = {}
            modid = backupreader.readModAttributes(mod)
            metadata = backupreader.readResourceMetadata(mod)
            if modid:
                objDict[modid] = metadata
                if metadata.has_key('file') and metadata['file']:
                    fn = metadata['file'].split('/')[-1]
                else:
                    fn = modid
                type = self.determineType(metadata, str(fn))
                portal = getUtility(ISiteRoot)
                utils = portal.plone_utils
                fn = utils.normalizeString(unquoteHTML(fn))
                objDict[modid]['id'] = fn
                objDict[modid]['type'] = type
                if modid in visibleids:
                    objDict[modid]['excludeFromNav'] = False
                else:
                    objDict[modid]['excludeFromNav'] = True
        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)
                                
def convertHTMLEntity(text):
    """Convert an HTML entity into a string"""
    if text.group(1)=='#':
        try:
            return chr(int(text.group(2)))
        except ValueError:
            return '&#%s;' % text.group(2)
    try:
        return htmlentitydefs.entitydefs[text.group(2)]
    except KeyError:
        return '&%s;' % text.group(2)

def unquoteHTML(text):
    """Convert an HTML quoted string into normal string.
    Works with &#XX; and with &nbsp; &gt; etc."""
    return re.sub(r'&(#?)(.+?);',convertHTMLEntity,text) 
