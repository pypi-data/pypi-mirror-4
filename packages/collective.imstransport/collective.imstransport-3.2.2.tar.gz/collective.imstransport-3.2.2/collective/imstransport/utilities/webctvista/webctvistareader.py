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
from configwebctvista import LOM_WEBCT_namespace, WEBCT_namespace, WEBCT_FILE_namespace

class WebCTVistaReader(object):

    def parseManifest(self, manifest):
        """ parse the manifest """
        return minidom.parseString(manifest)

    def readManifests(self, manifest):
        """ Read the manifests """
        manifests = manifest.getElementsByTagName('manifest')
        return manifests

    def readPackageMetadata(self, manifest):
        """ Read the package metadata """
        return self.readMetadata(manifest)

    def readOrganizations(self, manifest):
        """ Read the organizations section of the manifest. """
        orgs = {}
        organizations = manifest.getElementsByTagName('organizations')
        if organizations:
            organization_nodes = organizations[0].getElementsByTagName('organization')
            if organization_nodes:
                organization_node = organization_nodes[0]
                item_nodes = organization_nodes[0].getElementsByTagName('item')
                for item in item_nodes:
                    idref = item.getAttribute('identifierref')
                    titlenodes = item.getElementsByTagName('title')
                    if titlenodes:
                        orgs[idref] = self.getTextValue(titlenodes[0])
                    else:
                        orgs[idref] = None
        return orgs

    def readResources(self, manifest):
        """ Read all resources. """
        reslist = []
        resources = manifest.getElementsByTagName('resources')
        if resources:
            reslist =  resources[0].getElementsByTagName('resource')
        return reslist

    def getTextValue(self, node):
        """ Removes the text from the text_node of a node """
        for x in node.childNodes:
            if x.nodeType == x.TEXT_NODE:
                return x.nodeValue.strip()
        return None

    def readResourceAttributes(self, resource):
        """ Return attributes on resource node. """
        return (resource.getAttribute('identifier'),
                resource.getAttribute('type'),
                resource.getAttribute('href'))

    def readMetadata(self, metadata):
        md = {}
        self.readGeneral(metadata, md)
        self.readEducational(metadata, md)
        return md

    def readFiles(self, resource):
        files = []
        flns = resource.getElementsByTagName('file')
        if flns:
            for fln in flns:
                file = fln.getAttribute('href')
                if file:
                    files.append(file)
        return files

    def readGeneral(self, metadata, md):
        """ Read general node """
        gen_node = None
        gen_nodes = metadata.getElementsByTagNameNS(LOM_WEBCT_namespace, 'general')
        if gen_nodes:
            gen_node = gen_nodes[0]
            title_nodes = gen_node.getElementsByTagNameNS(LOM_WEBCT_namespace, 'title')        
            if title_nodes:
                langstring_nodes = title_nodes[0].getElementsByTagNameNS(LOM_WEBCT_namespace,'langstring')
                if langstring_nodes:
                    title = self.getTextValue(langstring_nodes[0])
                    if title:
                        md['title'] = title
            if not md.has_key('title'):
                raise ManifestError, 'Required tag "title" missing in lom/general metadata section for resource.'
            language_nodes = metadata.getElementsByTagNameNS(LOM_WEBCT_namespace, 'language')
            if language_nodes:
                lang = self.getTextValue(language_nodes[0])
                if lang:
                    md['language'] = lang
            desc_nodes = metadata.getElementsByTagNameNS(LOM_WEBCT_namespace, 'description')
            if desc_nodes:
                langstring_nodes = desc_nodes[0].getElementsByTagNameNS(LOM_WEBCT_namespace,'langstring')
                if langstring_nodes:
                    description = self.getTextValue(langstring_nodes[0])
                    if description:
                        md['description'] = description
            kw_nodes = metadata.getElementsByTagNameNS(LOM_WEBCT_namespace, 'keyword')
            if kw_nodes:
                kw_list = []
                for kw_node in kw_nodes:
                    kw_lang_nodes = kw_node.getElementsByTagNameNS(LOM_WEBCT_namespace,'langstring')
                    if kw_lang_nodes:
                        for lang_node in kw_lang_nodes:
                            kw = self.getTextValue(lang_node)
                            if kw:
                                kw_list.append(kw)
                if kw_list:
                    md['subject'] = kw_list

    def readEducational(self, metadata, md):
        """ Read Educational node """
        educational_node = None
        source = None
        value = None
        educational_nodes = metadata.getElementsByTagNameNS(LOM_WEBCT_namespace, 'educational')
        if educational_nodes:
            lrnodes = educational_nodes[0].getElementsByTagNameNS(LOM_WEBCT_namespace, 'learningresourcetype')
            if lrnodes:
                source_nodes = lrnodes[0].getElementsByTagNameNS(LOM_WEBCT_namespace, 'source')
                if source_nodes:
                    langstring_nodes = source_nodes[0].getElementsByTagNameNS(LOM_WEBCT_namespace, 'langstring')
                    if langstring_nodes:
                        source = self.getTextValue(langstring_nodes[0])
                value_nodes = lrnodes[0].getElementsByTagNameNS(LOM_WEBCT_namespace, 'value')
                if value_nodes:
                    langstring_nodes = value_nodes[0].getElementsByTagNameNS(LOM_WEBCT_namespace, 'langstring')
                    if langstring_nodes:
                        value = self.getTextValue(langstring_nodes[0])
            if source == 'WebCT' and value:
                md['webcttype'] = value

    def readContentMetadata(self, doc, md):
        """ Read the webct specific metadata """
        contobj_nodes = doc.getElementsByTagNameNS(WEBCT_namespace, 'ContentObject')
        if contobj_nodes:
            name_nodes = contobj_nodes[0].getElementsByTagNameNS(WEBCT_namespace, 'Name')
            path_nodes = contobj_nodes[0].getElementsByTagNameNS(WEBCT_FILE_namespace, 'Path')
            if name_nodes:
                md['id'] = self.getTextValue(name_nodes[0])
            if path_nodes:
                path = self.getTextValue(path_nodes[0])
                if path:
                    md['path'] = '/'.join(path.split('\\'))
                else:
                    md['path'] = ''

            
            
        
        

        
        
        
                



