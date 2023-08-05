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
LOM_version = 'LOMv1.0'

class CPResourceWriter:
    """ Writes resource and LOM metadata for the resource. """

    def __init__(self, writer):
        self.writer = writer
        self.resources_node = writer.resources_node
        self.lom_node = None

    def writeResource(self, resourceId, resource_type, path=None):
        """ Writes a resource object and adds LOM metadata """
        self.resource_node = self.writer._createNode(self.writer.resources_node,
                                         '',
                                         'resource',
                                         attrs=[('type', resource_type),
                                                ('identifier', resourceId),
                                                ('href',path)])

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
        identifier_node = self.writer._createNode(general_node, '', 'identifier', id)
        title_node = self.writer._createNode(general_node, '', 'title')
        self.writer._createNode(title_node,
                           '',
                           'langstring',
                           title,
                           [('xml:lang', lang)])
        if lang:
            self.writer._createNode(general_node, '', 'language', lang)
        if description:
            desc_node = self.writer._createNode(general_node, '', 'description')
            self.writer._createNode(desc_node,
                               '',
                               'langstring',
                               description,
                               [('xml:lang', lang)])
        if keywords:
            keyword_node = self. writer._createNode(general_node, '', 'keyword')
            for kw in keywords:
                self.writer._createNode(keyword_node,
                                   '',
                                   'langstring',
                                   kw,
                                   [('xml:lang', lang)])

    def writeLifeCycleNode(self, creators, contributors, modificationdate, lang=None):
        # lifeCycle Node
        self.lifecycle_node = self.writer._createNode(self.lom_node, '', 'lifecycle')

        if creators:
            self.createContributeElement(self.writer,
                                                  lang,
                                                  self.lifecycle_node,
                                                  LOM_version,
                                                  'author',
                                                  creators,
                                                  modificationdate)

        if contributors:
            self.createContributeElement(self.writer,
                                                  lang,
                                                  self.lifecycle_node,
                                                  LOM_version,
                                                  'unknown',
                                                  contributors,
                                                  modificationdate)


    def writeMetaMetadata(self, id, urlbase, email, modtime, lomversion, lang=None, contributors=[]):
        # MetaMetadata Node
        metametadata_node = self.writer._createNode(self.lom_node, '', 'metametadata')
        catalog_node = self.writer._createNode(metametadata_node, '', 'identifier')
        self.writer._createNode(catalog_node,
                           '',
                           'catalog',
                           '%s,%s' %(urlbase, email))
        entry_node = self.writer._createNode(catalog_node, '', 'entry')
        self.writer._createNode(entry_node,
                           '',
                           'langstring',
                           id,
                           [('xml:lang', lang)])
        if contributors:
            self.createContributeElement(self.writer,
                                         '',
                                         metametadata_node,
                                         LOM_version,
                                         'creator',
                                         contributors,
                                         modtime)        
        self.writer._createNode(metametadata_node, '', 'metadatascheme', LOM_version)
        if lang:
            self.writer._createNode(metametadata_node, '', 'language', lang)

    def writeTechnical(self, format, size, location):
        # Technical Node
        technical_node = self.writer._createNode(self.lom_node, '', 'technical')
        self.writer._createNode(technical_node, '', 'format', format)
        self.writer._createNode(technical_node, '', 'size', size)
        self.writer._createNode(technical_node, '', 'location', location)

    def writeRights(self, lomversion, value, copyright, lang=None): 
        # Rights Node
        rights_node = self.writer._createNode(self.lom_node, '', 'rights')
        copyright_other_node = self.writer._createNode(rights_node,
                                                  '',
                                                  'copyrightandotherrestrictions')
        source_node = self.writer._createNode(copyright_other_node, '', 'source')
        self.writer._createNode(source_node,
                           '',
                           'langstring',
                           LOM_version,
                           [('xml:lang', lang)])
        value_node = self.writer._createNode(copyright_other_node, '', 'value')
        self.writer._createNode(value_node,
                           '',
                           'langstring',
                           value,
                           [('xml:lang', lang)])
        description_node = self.writer._createNode(rights_node, '', 'description')
        self.writer._createNode(description_node,
                           '',
                           'langstring',
                           copyright,
                           [('xml:lang', lang)])

    def writeFileNode(self, path):
        # File Node
        self.writer._createNode(self.resource_node, '', 'file', attrs=[('href',path)])

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

    def createContributeElement(self, writer, lang, lc_node, source, value, entities, date, email=None):

        contribute_node = writer._createNode(lc_node, '', 'contribute')
        role_node = writer._createNode(contribute_node, '', 'role')
        source_node = writer._createNode(role_node, '', 'source')
        writer._createNode(source_node,'','langstring', source,[('xml:lang', lang)])
        value_node = writer._createNode(role_node, '', 'value')
        writer._createNode(value_node, '', 'langstring', value, [('xml:lang', lang)])
        if entities:
            if type(entities) not in [type([]), type(())]:
                entities = [entities]
            for e in entities:
                centity_node = writer._createNode(contribute_node, '', 'centity')
                writer._createNode(centity_node,
                                   '',
                                   'vcard',
                                   self.createVCard(e, email))
        if date:
            date_node = writer._createNode(contribute_node, '', 'date')
            writer._createNode(date_node, '', 'datetime', date)
