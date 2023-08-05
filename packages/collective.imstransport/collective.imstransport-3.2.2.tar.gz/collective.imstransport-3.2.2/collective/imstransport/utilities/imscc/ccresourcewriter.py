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

class CCResourceWriter:
    """ Writes resource and LOM metadata for the resource. """

    def __init__(self, writer):
        self.writer = writer
        self.resources_node = writer.resources_node
        self.lom_node = None

    def writeResource(self, resourceId, resource_type, path=None):
        """ Writes a resource object and adds LOM metadata """

        if path:
            self.resource_node = self.writer._createNode(self.writer.resources_node,
                                         '',
                                         'resource',
                                         attrs=[('type', resource_type),
                                                ('identifier', resourceId),
                                                ('href',path)])
        else:
            self.resource_node = self.writer._createNode(self.writer.resources_node,
                                         '',
                                         'resource',
                                         attrs=[('type', resource_type),
                                                ('identifier', resourceId)])




    def writeLOMMetadata(self):
        """ Write out the metadata. """
        self.lommetadata_node = self.writer._createNode(self.resource_node, '', 'metadata')

    def writeLOMNode(self, lom_namespace):
        """ Write the lom node """   
        self.lom_node = self.writer._createNode(self.lommetadata_node,
                                      lom_namespace,
                                      'lom',
                                      attrs=[('xmlns', lom_namespace)])
        
    def writeGeneralNode(self, id, title, urlbase, lang=None, description=None, keywords=[]):

        # General Node
        general_node = self.writer._createNode(self.lom_node, '', 'general')
        identifier_node = self.writer._createNode(general_node, '', 'identifier')
        self.writer._createNode(identifier_node,
                           '',
                           'catalog',
                           urlbase)
        self.writer._createNode(identifier_node, '', 'entry', id)
        title_node = self.writer._createNode(general_node, '', 'title')
        self.writer._createNode(title_node,
                           '',
                           'string',
                           title,
                           [('xml:lang', lang)])
        if lang:
            self.writer._createNode(general_node, '', 'language', lang)
        if description:
            desc_node = self.writer._createNode(general_node, '', 'description')
            self.writer._createNode(desc_node,
                               '',
                               'string',
                               description,
                               [('xml:lang', lang)])
        if keywords:
            keyword_node = self. writer._createNode(general_node, '', 'keyword')
            for kw in keywords:
                self.writer._createNode(keyword_node,
                                   '',
                                   'string',
                                   kw,
                                   [('xml:lang', lang)])

    def writeLifeCycleNode(self):
        # lifeCycle Node
        self.lifecycle_node = self.writer._createNode(self.lom_node, '', 'lifeCycle')


    def writeMetaMetadata(self, id, urlbase, email, modtime, lomversion, lang=None, contributors=[]):
        # MetaMetadata Node
        metametadata_node = self.writer._createNode(self.lom_node, '', 'metaMetadata')
        catalog_node = self.writer._createNode(metametadata_node, '', 'identifier')
        self.writer._createNode(catalog_node,
                           '',
                           'catalog',
                           '%s,%s' %(urlbase, email))
        entry_node = self.writer._createNode(catalog_node, '', 'entry', id)
        if contributors:
            self.createContributeElement(self.writer,
                                         '',
                                         metametadata_node,
                                         '',
                                         'creator',
                                         contributors,
                                         modtime)        
            self.writer._createNode(metametadata_node, '', 'metadataSchema', lomversion)

        if lang:
            self.writer._createNode(metametadata_node, '', 'language', lang)

    def writeTechnical(self, format, size, location):
        # Technical Node
        technical_node = self.writer._createNode(self.lom_node, '', 'technical')
        self.writer._createNode(technical_node, '', 'format', format)
        self.writer._createNode(technical_node, '', 'size', size)
        self.writer._createNode(technical_node, '', 'location', location)

    def writeRights(self, lomversion, value, copyright): 
        # Rights Node
        rights_node = self.writer._createNode(self.lom_node, '', 'rights')
        copyright_other_node = self.writer._createNode(rights_node,
                                                  '',
                                                  'copyrightAndOtherRestrictions')
        source_node = self.writer._createNode(copyright_other_node, '', 'source', lomversion)           
        value_node = self.writer._createNode(copyright_other_node, '', 'value', value)
        description_node = self.writer._createNode(rights_node, '', 'description')
        self.writer._createNode(description_node,
                           '',
                           'string',
                           copyright,
                           [('xml:lang', 'x-none')])

    def writeFileNode(self, path):
        # File Node
        self.writer._createNode(self.resource_node, '', 'file', attrs=[('href',path)])

    def createContributeElement(self, writer, nspace, lc_node, source, value, entities=[], date=None, email=None):
        """ writes out a Contribute Element """
        contribute_node = writer._createNode(lc_node, nspace, 'contribute')
        role_node = writer._createNode(contribute_node, nspace, 'role')
        source_node = writer._createNode(role_node, nspace, 'source', source)
        value_node = writer._createNode(role_node, nspace, 'value', value)
        if entities:
            if type(entities) not in [type([]), type(())]:
                entities = [entities]
            for e in entities:
                centity_node = writer._createNode(contribute_node, nspace, 'entity',self.createVCard(e,email))
        if date:
            date_node = writer._createNode(contribute_node, nspace, 'date')
            self.writer._createNode(date_node, nspace, 'dateTime', date)

    def createVCard(self, name, email=None):
        """
        Writes out a VCard entry for a contribute element
        
        Note: Should replace this with the python vcard library.
        
        """
        vCard = 'BEGIN:VCARD\n'
        vCard += 'FN:'+name+'\n'
        if email:
            vCard += 'EMAIL;INTERNET:'+email+'\n'
        vCard += 'END:VCARD'
        return vCard

    def writeCustomMetadata(self, object):
        """ 
        Hook for writing custom metadata for additional metatdata requirements. 
        Should return standards compliant xml that relates to object passed in.
        """
        return

    def getLinkXml(self, ns, schemainst, title, link):
        """ Return text for a file that stores the link in an xml file """
        doc = minidom.Document()
        wlnode = self.writer._createNode(doc, ns, 'webLink', attrs=[('xmlns:xsi', schemainst),('xmlns',ns)])
        self.writer._createNode(wlnode, '', 'title', value=title)
        self.writer._createNode(wlnode, '', 'url', attrs=[('href',link),('target','_blank')])
        return wlnode.toxml('utf-8')
