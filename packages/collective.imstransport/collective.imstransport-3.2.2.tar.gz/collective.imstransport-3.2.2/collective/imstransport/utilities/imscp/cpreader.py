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
from configcp import LOM_IMSCP_namespace

class CPReader(object):

    def parseManifest(self, manifest):
        """ parse the manifest """
        return minidom.parseString(manifest)

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
                itemnum = 1
                for item in item_nodes:
                    idref = item.getAttribute('identifierref')
                    titlenodes = item.getElementsByTagName('title')
                    if titlenodes:
                        orgs[idref] = (itemnum, self.getTextValue(titlenodes[0]))
                    else:
                        orgs[idref] = (itemnum, None)
                    itemnum += 1
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
        self.readLifecycle(metadata, md)
        self.readMetaMetadata(metadata, md)
        self.readTechnical(metadata, md)
        self.readRights(metadata, md)
        return md

    def readFiles(self, resource):
        files = []
        flns = resource.getElementsByTagName('file')
        if flns:
            for fln in flns:
                file = fln.getAttribute('href')
                files.append(file)
        return files

    def readGeneral(self, metadata, md):
        """ Read general node """
        gen_node = None
        gen_nodes = metadata.getElementsByTagNameNS(LOM_IMSCP_namespace, 'general')
        if gen_nodes:
            gen_node = gen_nodes[0]
            title_nodes = gen_node.getElementsByTagNameNS(LOM_IMSCP_namespace, 'title')        
            if title_nodes:
                langstring_nodes = title_nodes[0].getElementsByTagNameNS(LOM_IMSCP_namespace,'langstring')
                if langstring_nodes:
                    title = self.getTextValue(langstring_nodes[0])
                    if title:
                        md['title'] = title
            if not md.has_key('title'):
                raise ManifestError, 'Required tag "title" missing in lom/general metadata section for resource.'
            language_nodes = metadata.getElementsByTagNameNS(LOM_IMSCP_namespace, 'language')
            if language_nodes:
                lang = self.getTextValue(language_nodes[0])
                if lang:
                    md['language'] = lang
            desc_nodes = metadata.getElementsByTagNameNS(LOM_IMSCP_namespace, 'description')
            if desc_nodes:
                langstring_nodes = desc_nodes[0].getElementsByTagNameNS(LOM_IMSCP_namespace,'langstring')
                if langstring_nodes:
                    description = self.getTextValue(langstring_nodes[0])
                    if description:
                        md['description'] = description
            kw_nodes = metadata.getElementsByTagNameNS(LOM_IMSCP_namespace, 'keyword')
            if kw_nodes:
                kw_list = []
                for kw_node in kw_nodes:
                    kw_lang_nodes = kw_node.getElementsByTagNameNS(LOM_IMSCP_namespace,'langstring')
                    if kw_lang_nodes:
                        for lang_node in kw_lang_nodes:
                            kw = self.getTextValue(lang_node)
                            if kw:
                                kw_list.append(kw)
                if kw_list:
                    md['subject'] = kw_list
    
    def readLifecycle(self, metadata, md):
        """ Read Lifecycle node """
        lc_node = None
        lc_nodes = metadata.getElementsByTagNameNS(LOM_IMSCP_namespace, 'lifecycle')
        if lc_nodes:
            lc_node = lc_nodes[0]
        if lc_node:
            # Lifecycle Node
            contribute_nodes = lc_node.getElementsByTagNameNS(LOM_IMSCP_namespace, 'contribute')
            # For each contribute node there is a role node, a centity node, and possibly a date node
            for contribute_node in contribute_nodes:
                source = ''
                value = ''
                vlist = []
                datetime = ''
                role_nodes = contribute_node.getElementsByTagNameNS(LOM_IMSCP_namespace, 'role')
                if role_nodes:
                    source_nodes = role_nodes[0].getElementsByTagNameNS(LOM_IMSCP_namespace, 'source')
                    if source_nodes:
                        langstring_nodes = source_nodes[0].getElementsByTagNameNS(LOM_IMSCP_namespace, 'langstring')
                        if langstring_nodes:
                            source = self.getTextValue(langstring_nodes[0])
                    value_nodes = role_nodes[0].getElementsByTagNameNS(LOM_IMSCP_namespace, 'value')
                    if value_nodes:
                        langstring_nodes = value_nodes[0].getElementsByTagNameNS(LOM_IMSCP_namespace, 'langstring')
                        if langstring_nodes:
                            value = self.getTextValue(langstring_nodes[0])
                entity_nodes = contribute_node.getElementsByTagNameNS(LOM_IMSCP_namespace, 'centity')
                for entity_node in entity_nodes:
                    vcard = entity_node.getElementsByTagNameNS(LOM_IMSCP_namespace, 'vcard')
                    if vcard:
                        name, email = self.getVcardValues(vcard[0])
                        if value:
                            vlist.append((name, email))
                date_nodes = contribute_node.getElementsByTagNameNS(LOM_IMSCP_namespace, 'date')
                if date_nodes:
                    datetime_nodes = date_nodes[0].getElementsByTagNameNS(LOM_IMSCP_namespace, 'datetime')
                    if datetime_nodes:
                        datetime = self.getTextValue(datetime_nodes[0])
                # Creator
                if 'author' == value.lower() and vlist:
                    md['creators'] = [x[0] for x in vlist]
                    if datetime:
                        md['creation_date'] = datetime
                # Contributors
                if 'unknown' == value.lower() and vlist:
                    md['contributors'] = [x[0] for x in vlist]

    def readMetaMetadata(self, metadata, md):
        """ Read MetaMetadata node """

    def readTechnical(self, metadata, md):
        """ Read the Technical node """
        tec_node = None
        tec_nodes = metadata.getElementsByTagNameNS(LOM_IMSCP_namespace, 'technical')
        if tec_nodes:
            tec_node = tec_nodes[0]
            format_nodes = tec_node.getElementsByTagNameNS(LOM_IMSCP_namespace, 'format')
            if format_nodes:
                format = self.getTextValue(format_nodes[0])
                if format:
                    md['Format'] = format

    def readRights(self, metadata, md):
        """ Read Rights node """
        rights_node = None
        rights_nodes = metadata.getElementsByTagNameNS(LOM_IMSCP_namespace, 'rights')
        if rights_nodes:
            rights_node = rights_nodes[0]
            description_nodes = rights_node.getElementsByTagNameNS(LOM_IMSCP_namespace,'description')
            if description_nodes:
                langstring_nodes = description_nodes[0].getElementsByTagNameNS(LOM_IMSCP_namespace,'langstring')
                if langstring_nodes:
                    description = self.getTextValue(langstring_nodes[0])
                    if description:
                        md['rights'] = description

    def getVcardValues(self, node):
        """
        Looks for the full name and email values in a VCARD value.
        """
        text = self.getTextValue(node)
        textlines = text.strip().split('\n')
        value = self.getVcardValue('BEGIN', [textlines[0]])
        if 'VCARD' != value.strip().upper():
            raise ManifestError, 'Missing VCARD BEGIN tag'
        value = self.getVcardValue('END', [textlines[-1]])
        if 'VCARD' != value.strip().upper():
            raise ManifestError, 'Missing VCARD END tag'
        name = self.getVcardValue('FN', textlines)
        email = self.getVcardValue('EMAIL;INTERNET', textlines)
        return name, email
        
    def getVcardValue(self, field, text):
        """ Try to get a value for a VCARD field. """
        for textline in text:
            textline = textline.strip()
            if textline.find(':'):
                tag = textline.split(':')
                if field == tag[0].upper().strip():
                    return tag[1].strip()
        else:
            return ''


