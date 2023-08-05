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
from configcc import LOM_namespace, LOM_IMSCC_namespace, WL_namespace

class CCReader(object):

    def parseManifest(self, manifest):
        """ parse the manifest """
        return minidom.parseString(manifest)

    def readPackageMetadata(self, manifest, pmd):
        """ Read the package metadata """
        metadata = manifest.getElementsByTagName('metadata')
        if metadata:
            lomcc = metadata[0].getElementsByTagNameNS(LOM_IMSCC_namespace, 'lom')
            if lomcc:
                gen_nodes = lomcc[0].getElementsByTagName('general')
                if gen_nodes:
                    title_nodes = gen_nodes[0].getElementsByTagName('title')        
                    if title_nodes:
                        langstring_nodes = title_nodes[0].getElementsByTagName('string')
                        if langstring_nodes:
                            title = self.getTextValue(langstring_nodes[0])
                            if title:
                                pmd['title'] = title
                    language_nodes = gen_nodes[0].getElementsByTagName('language')
                    if language_nodes:
                        lang = self.getTextValue(language_nodes[0])
                        if lang:
                            pmd['language'] = lang
                    desc_nodes = gen_nodes[0].getElementsByTagName('description')
                    if desc_nodes:
                        langstring_nodes = desc_nodes[0].getElementsByTagName('string')
                        if langstring_nodes:
                            description = self.getTextValue(langstring_nodes[0])
                            if description:
                                pmd['description'] = description
                    kw_nodes = gen_nodes[0].getElementsByTagName('keyword')
                    if kw_nodes:
                        kw_lang_nodes = kw_nodes[0].getElementsByTagName('string')
                        kw_list = []
                        if kw_lang_nodes:
                            for lang_node in kw_lang_nodes:
                                kw = self.getTextValue(lang_node)
                                if kw:
                                    kw_list.append(kw)
                        if kw_list:
                            pmd['subject'] = kw_list

    def readOrganizations(self, manifest):
        """ Read the organizations section of the manifest. """
        orgs = {}
        organizations = manifest.getElementsByTagName('organizations')
        if organizations:
            organization_nodes = organizations[0].getElementsByTagName('organization')
            if organization_nodes:
                organization_node = organization_nodes[0]
                item_nodes = organization_nodes[0].getElementsByTagName('item')
                itemnum = 0
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
        gen_nodes = metadata.getElementsByTagNameNS(LOM_namespace, 'general')
        if gen_nodes:
            gen_node = gen_nodes[0]
            title_nodes = gen_node.getElementsByTagNameNS(LOM_namespace, 'title')        
            if title_nodes:
                langstring_nodes = title_nodes[0].getElementsByTagNameNS(LOM_namespace,'string')
                if langstring_nodes:
                    title = self.getTextValue(langstring_nodes[0])
                    if title:
                        md['title'] = title
            if not md.has_key('title'):
                raise ManifestError, 'Required tag "title" missing in lom/general metadata section for resource.'
            language_nodes = metadata.getElementsByTagNameNS(LOM_namespace, 'language')
            if language_nodes:
                lang = self.getTextValue(language_nodes[0])
                if lang:
                    md['language'] = lang
            desc_nodes = metadata.getElementsByTagNameNS(LOM_namespace, 'description')
            if desc_nodes:
                langstring_nodes = desc_nodes[0].getElementsByTagNameNS(LOM_namespace,'string')
                if langstring_nodes:
                    description = self.getTextValue(langstring_nodes[0])
                    if description:
                        md['description'] = description
            kw_nodes = metadata.getElementsByTagNameNS(LOM_namespace, 'keyword')
            if kw_nodes: 
                kw_list = []
                for kw_node in kw_nodes:
                    kw_lang_nodes = kw_node.getElementsByTagNameNS(LOM_namespace,'string')
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
        lc_nodes = metadata.getElementsByTagNameNS(LOM_namespace, 'lifeCycle')

        if lc_nodes:
            lc_node = lc_nodes[0]

        if lc_node:
            # Lifecycle Node
            contribute_nodes = lc_node.getElementsByTagNameNS(LOM_namespace, 'contribute')

            # For each contribute node there is a role node, a centity node, and possibly a date node
            for contribute_node in contribute_nodes:
                source = ''
                value = ''
                vlist = []
                datetime = ''

                role_nodes = contribute_node.getElementsByTagNameNS(LOM_namespace, 'role')
                if role_nodes:
                    source_nodes = role_nodes[0].getElementsByTagNameNS(LOM_namespace, 'source')
                    if source_nodes:
                        langstring_nodes = source_nodes[0].getElementsByTagNameNS(LOM_namespace, 'string')
                        if langstring_nodes:
                            source = self.getTextValue(langstring_nodes[0])
                    value_nodes = role_nodes[0].getElementsByTagNameNS(LOM_namespace, 'value')
                    if value_nodes:
                        langstring_nodes = value_nodes[0].getElementsByTagNameNS(LOM_namespace, 'string')
                        if langstring_nodes:
                            value = self.getTextValue(langstring_nodes[0])

                entity_nodes = contribute_node.getElementsByTagNameNS(LOM_namespace, 'entity')
                for entity_node in entity_nodes:
                    name, email = self.getVcardValues(entity_node)
                    if value:
                        vlist.append((name, email))
                            
                date_nodes = contribute_node.getElementsByTagNameNS(LOM_namespace, 'date')
                if date_nodes:
                    datetime_nodes = date_nodes[0].getElementsByTagNameNS(LOM_namespace, 'dateTime')
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
        """ Read Meta-metadata node """
        pass


    def readTechnical(self, metadata, md):
        """ Read Technical node """
        tec_node = None
        tec_nodes = metadata.getElementsByTagNameNS(LOM_namespace, 'technical')

        if tec_nodes:
            tec_node = tec_nodes[0]

            format_nodes = tec_node.getElementsByTagNameNS(LOM_namespace, 'format')
            if format_nodes:
                format = self.getTextValue(format_nodes[0])
                if format:
                    md['Format'] = format

    def readRights(self, metadata, md):
        """ Read Rights node """
        rights_node = None
        rights_nodes = metadata.getElementsByTagNameNS(LOM_namespace, 'rights')

        if rights_nodes:
            rights_node = rights_nodes[0]
            description_nodes = rights_node.getElementsByTagNameNS(LOM_namespace,'description')
            if description_nodes:
                langstring_nodes = description_nodes[0].getElementsByTagNameNS(LOM_namespace,'string')
                if langstring_nodes:
                    description = self.getTextValue(langstring_nodes[0])
                    if description:
                        md['rights'] = description

    def getLinkInfo(self, linkfile):
        """ Read an anchor tag and return the link """
        linkdict = {}
        doc = minidom.parseString(linkfile)
        title = ''
        link = ''
        link_nodes = doc.getElementsByTagNameNS(WL_namespace, 'webLink')
        if link_nodes:
            title_nodes = link_nodes[0].getElementsByTagName('title')
            url_nodes = link_nodes[0].getElementsByTagName('url')
            if title_nodes:
                title = self.getTextValue(title_nodes[0])
                if url_nodes:
                    link = url_nodes[0].getAttribute('href')

        return title, link


    def getVcardValues(self, node):
        """
        Looks for the full name and email values in a VCARD element.
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


