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

class CPResourceReader(object):

    def __init__(self, reader, id, lom_namespace):
        """
        """
        self.id = id
        self.reader = reader
        self.document = self.reader.document
        self.resource = None
        self.files = []
        self.resdict = {}
        self.href = ''
        self.lom_node = None
        self.lom_namespace = lom_namespace

        resources = self.document.getElementsByTagName('resources')
        if resources:
            for res in resources[0].getElementsByTagName('resource'):
                if self.id == res.getAttribute('identifier'):
                    self.resource = res
                    self.href = res.getAttribute('href')
                    lom_nodes = self.resource.getElementsByTagNameNS(self.lom_namespace, 'lom')
                    if lom_nodes:
                        self.lom_node = lom_nodes[0]
                    break

        if not self.resource:
            raise ManifestError, 'No resource found for %s.' %resid


    def getHref(self):
        """ Get href value from resource reader """
        return self.href


    def readFiles(self):
        """ Read the files from the resource node """

        files = []
        file_nodes = self.resource.getElementsByTagName('file')
        fn = ''
        for f in file_nodes:
            fn = f.getAttribute('href')  
            if fn: 
                self.files.append(fn)

        return self.files

    def appendCustomData(self, metaDictionary):
        """ Read the custom fields in dictionary and save on to object """
        self.resdict.update(metaDictionary)
        return

    def readGeneral(self):
        """ Read general node """

        gen_node = None
        gen_nodes = self.lom_node.getElementsByTagNameNS(self.lom_namespace, 'general')

        if gen_nodes:
            gen_node = gen_nodes[0]

            title_nodes = gen_node.getElementsByTagNameNS(self.lom_namespace, 'title')        
            if title_nodes:
                langstring_nodes = self.readStringNodes(title_nodes[0]) 
                if langstring_nodes:
                    title = self.reader.getTextValue(langstring_nodes[0])
                    if title:
                        self.resdict['title'] = title

            if not self.resdict.has_key('title'):
                raise ManifestError, 'Required tag "title" missing in lom/general metadata section for resource %s.' %resid

            language_nodes = self.lom_node.getElementsByTagNameNS(self.lom_namespace, 'language')
            if language_nodes:
                lang = self.reader.getTextValue(language_nodes[0])
                if lang:
                    self.resdict['language'] = lang

            desc_nodes = self.lom_node.getElementsByTagNameNS(self.lom_namespace, 'description')
            if desc_nodes:
                langstring_nodes = self.readStringNodes(desc_nodes[0])
                if langstring_nodes:
                    description = self.reader.getTextValue(langstring_nodes[0])
                    if description:
                        self.resdict['description'] = description

            kw_nodes = self.lom_node.getElementsByTagNameNS(self.lom_namespace, 'keyword')
            if kw_nodes:
                kw_lang_nodes = self.readStringNodes(kw_nodes[0])
                kw_list = []
                if kw_lang_nodes:
                    for lang_node in kw_lang_nodes:
                        kw = self.reader.getTextValue(lang_node)
                        if kw:
                            kw_list.append(kw)
                if kw_list:
                    self.resdict['subject'] = kw_list


    def readLifecycle(self):
        """ Read Lifecycle node """


        lc_node = None
        lc_nodes = self.readCamelCaseNode(self.lom_node, 'lifeCycle')

        if lc_nodes:
            lc_node = lc_nodes[0]

        if lc_node:
            # Lifecycle Node
            contribute_nodes = lc_node.getElementsByTagNameNS(self.lom_namespace, 'contribute')

            # For each contribute node there is a role node, a centity node, and possibly a date node
            for contribute_node in contribute_nodes:
                source = ''
                value = ''
                vlist = []
                date = ''

                role_nodes = contribute_node.getElementsByTagNameNS(self.lom_namespace, 'role')
                if role_nodes:
                    source_nodes = role_nodes[0].getElementsByTagNameNS(self.lom_namespace, 'source')
                    if source_nodes:
                        langstring_nodes = self.readStringNodes(source_nodes[0]) 
                        if langstring_nodes:
                            source = self.reader.getTextValue(langstring_nodes[0])
                    value_nodes = role_nodes[0].getElementsByTagNameNS(self.lom_namespace, 'value')
                    if value_nodes:
                        langstring_nodes =  self.readStringNodes(value_nodes[0])
                        if langstring_nodes:
                            value = self.reader.getTextValue(langstring_nodes[0])

                centity_nodes = self.readEntityNode(contribute_node)
                for centity_node in centity_nodes:
                    for cnode in centity_node.childNodes:
                        if cnode.nodeType == cnode.ELEMENT_NODE:
                            name, email = self.reader.getVcardValues(cnode, self.id)
                            if value:
                                vlist.append((name, email))

                date_nodes = contribute_node.getElementsByTagNameNS(self.lom_namespace, 'date')
                if date_nodes:
                    datetime_nodes = date_nodes[0].getElementsByTagNameNS(self.lom_namespace, 'datetime')
                    if datetime_nodes:
                        datetime = self.reader.getTextValue(datetime_nodes[0])            

                # Creator
                if 'author' == value.lower() and vlist:
                    self.resdict['creators'] = [x[0] for x in vlist]
                    if date:
                        self.resdict['creation_date'] = date

                # Contributors
                if 'unknown' == value.lower() and vlist:
                    self.resdict['contributors'] = [x[0] for x in vlist]


    def readMetaMetadata(self):
        """ Read Meta-metadata node """
        pass


    def readTechnical(self):
        """ Read Technical node """
        tec_node = None
        tec_nodes = self.lom_node.getElementsByTagNameNS(self.lom_namespace, 'technical')

        if tec_nodes:
            tec_node = tec_nodes[0]

            format_nodes = tec_node.getElementsByTagNameNS(self.lom_namespace, 'format')
            if format_nodes:
                format = self.reader.getTextValue(format_nodes[0])
                if format:
                    self.resdict['Format'] = format

    def readRights(self):
        """ Read Rights node """

        rights_node = None
        rights_nodes = self.lom_node.getElementsByTagNameNS(self.lom_namespace, 'rights')

        if rights_nodes:
            rights_node = rights_nodes[0]

            description_nodes = rights_node.getElementsByTagNameNS(self.lom_namespace,'description')
            if description_nodes:
                langstring_nodes = self.readStringNodes(description_nodes[0])
                if langstring_nodes:
                    description = self.reader.getTextValue(langstring_nodes[0])
                    if description:
                        self.resdict['rights'] = description

    def getFilePaths(self):
        """ Get File Ids """
        return self.files

    def readLink(self, html):
        """ Read an anchor tag and return the link """
        doc = minidom.parseString(html)
        anchor_nodes = doc.getElementsByTagName('a')
        if anchor_nodes:
            return anchor_nodes[0].getAttribute('href')
        return None
        
    def processResourceMetadata(self):
        """ Process the metadata for this resource """
        return self.resdict

    def getCustomData(self, tagname, ns):
        """ Get the custom data for xml processing """
        custom_elem = self.resource.getElementsByTagNameNS(ns, tagname)
        if custom_elem:
            return custom_elem[0]
        else:
            return []

    def readStringNodes(self, node):
        """ Get the langstring or string node (depending on implementation) """
        langstring_nodes = node.getElementsByTagNameNS(self.lom_namespace,'langstring')
        if not langstring_nodes:
            langstring_nodes = node.getElementsByTagNameNS(self.lom_namespace,'string')

        return langstring_nodes

    def readCamelCaseNode(self, node, element):
        """ Check for camel case and lower case versions of certain elements """

        retnodes = node.getElementsByTagNameNS(self.lom_namespace, element)
        if not retnodes:
            retnodes = node.getElementsByTagNameNS(self.lom_namespace, element.lower())

        return retnodes

    def readEntityNode(self, node):
        """ Read in either the centity or entity tags """

        centity_nodes = node.getElementsByTagNameNS(self.lom_namespace, 'centity')
        if not centity_nodes:
            centity_nodes = node.getElementsByTagNameNS(self.lom_namespace, 'entity')

        return centity_nodes
        
        



