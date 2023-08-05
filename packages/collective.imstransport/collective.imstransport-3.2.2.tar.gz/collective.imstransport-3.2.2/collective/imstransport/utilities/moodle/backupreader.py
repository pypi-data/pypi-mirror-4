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

from xml.dom import minidom
from collective.imstransport.IMS_exceptions import ManifestError
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup

class BackupReader(object):

    def parseMoodleXML(self, moodlexml):
        """ Parse the moodle xml doc """
        doc = minidom.parseString(moodlexml)
        moodlebackup = doc.getElementsByTagName('MOODLE_BACKUP')
        if moodlebackup:
            return moodlebackup[0]
        else:
            return None
            
    def readMods(self, main):
        """ Return a list of the resource modules """
        modlist = []
        modules = main.getElementsByTagName('MODULES')
        if modules:
            mods = modules[0].getElementsByTagName('MOD')
            for mod in mods:
                type = mod.getElementsByTagName('MODTYPE')[0]
                if self.getTextValue(type) == 'resource':
                    modlist.append(mod)
        return modlist

    def readModAttributes(self, mod):
        """ Return the id of the current module """
        id_elem = mod.getElementsByTagName('ID')[0]
        if id_elem:
            return self.getTextValue(mod.getElementsByTagName('ID')[0])
        else:
            return ''

    def readSections(self, main):
        """ Returns a list of visible resources  """
        visids = []
        sections = main.getElementsByTagName('SECTIONS')
        if sections:
            sectionelements = sections[0].getElementsByTagName('SECTION')
            for sectionelement in sectionelements:
                mods = sectionelement.getElementsByTagName('MODS')
                if mods:
                    modelements = mods[0].getElementsByTagName('MOD')
                    for modelement in modelements:
                        # If the resource module is marked visible within
                        # a top level (indent) then place it in navigation.
                        type = modelement.getElementsByTagName('TYPE')[0]
                        if self.getTextValue(type) == 'resource':
                            if self.getTextValue(modelement.getElementsByTagName('VISIBLE')[0]) == '1':
                                if self.getTextValue(modelement.getElementsByTagName('INDENT')[0]) == '0':
                                    id = self.getTextValue(modelement.getElementsByTagName('INSTANCE')[0])
                                    if id not in visids:
                                        visids.append(id)
        return visids

    def readResourceMetadata(self, mod):
        """ Read in the resource module """
        metadata = {}
        reference = ''
        refnode = mod.getElementsByTagName('REFERENCE')
        if refnode and self.getTextValue(refnode[0]):
            reference = self.getTextValue(refnode[0])
            if reference:
                reference = self.runFilters(reference, ['variables'])
        title = mod.getElementsByTagName('NAME')
        metadata['title'] = self.getTextValue(title[0])
        type = self.getTextValue(mod.getElementsByTagName('TYPE')[0])
        if type == 'text':
            metadata['Format'] = 'text/plain'
        elif type == 'html':
            metadata['Format'] = 'text/html'
        elif type == 'file' and reference:
            parsedurl = urlparse(reference)
            if parsedurl[0]:
                metadata['remoteUrl'] = reference
                metadata['type'] = 'Link'
            else:
                metadata['file'] = 'course_files/%s' %reference
        else:
            metadata['Format'] = 'text/html'
            metadata['text'] = ''
        summary = mod.getElementsByTagName('SUMMARY')
        if summary:
            descrip = self.getTextValue(summary[0])
            if descrip:
                metadata['description'] = self.runFilters(descrip, ['striphtml'])
        alltext = mod.getElementsByTagName('ALLTEXT')
        if alltext:
            text = self.getTextValue(alltext[0])
            if text:
                metadata['text'] = self.runFilters(text, ['variables'])
        metadata['path'] = ''
        return metadata

    def runFilters(self, text, filters):
        """ Run a filter over the links """
        rettext = text
        if 'variables' in filters:
            rettext = self.removeMoodleVariables(rettext)
        if 'striphtml' in filters:
            rettext = self.stripHTML(rettext)
        return rettext
        
    def removeMoodleVariables(self, text):
        """ Remove all the moodle variables """
        import re
        return re.sub('\$@.*@\$','', text)
    
    def stripHTML(self, text):
        """ Remove all html tags and return the inner text """
        import re
        return re.sub('<([^!>]([^>]|\n)*)>','', text)

    def getTextValue(self, node):
        """ Removes the text from the text_node of a node """
        for x in node.childNodes:
            if x.nodeType == x.TEXT_NODE:
                return x.nodeValue.strip()
        return None
