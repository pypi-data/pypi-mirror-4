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
from string import join
import md5
import os
from configcc import IMS_schema, IMS_version, LOM_version, LOM_namespace, LOM_IMSCC_namespace, WL_namespace
from configcc import WL_namespace, IMS_schemainst
from configcc import namespaces, schema_locations

class CCWriter(object):

    def __init__(self):
        self.document = minidom.Document()

    def createManifest(self, id, ver):
        """ Create a new empty manifest. """
        doc = minidom.Document()
        manifest = self._createNode(doc, '', 'manifest', 
                         attrs=[('identifier', id),
                                ('xmlns:version', ver),])
        self.addNamespaces(manifest, namespaces)
        self.addSchemaLocations(manifest, schema_locations)
        return doc

    def writeTopLevelMetadata(self, doc, id, title, urlbase, lang, desc=None, keywords=None):
        """ Write top level metadata into the manifest. """
        manifest = doc.getElementsByTagName('manifest')
        if manifest:
            md = self._createNode(manifest[0], '', 'metadata')
            self._createNode(md, '', 'schema', IMS_schema)
            self._createNode(md, '', 'schemaversion', IMS_version)
            lom = self._createNode(md, LOM_IMSCC_namespace, 'lom')
            gen = self._createNode(lom, '', 'general')
            ident = self._createNode(gen, '', 'identifier')
            self._createNode(ident, '', 'catalog', urlbase)
            self._createNode(ident, '', 'entry', id)
            tn = self._createNode(gen, '', 'title')
            self._createNode(tn, '', 'string', title, [('xml:lang', lang)])
            self._createNode(gen, '', 'language', lang)
            if desc:
                dn = self._createNode(gen, '', 'description')
                self._createNode(dn, '', 'string', desc, [('xml:lang', lang)])
            if keywords:
                kn = self._createNode(gen, '', 'keyword')
                for kw in keywords:
                    self._createNode(kn, '', 'string', kw, [('xml:lang', lang)])
        
    def createOrganizations(self, doc, orgId, itemId):
        """ Create an organizations section in the manifest """
        manifest = doc.getElementsByTagName('manifest')
        if manifest:
            orgs = self._createNode(manifest[0], '', 'organizations')
            org = self._createNode(orgs, '', 'organization', attrs=[('identifier', orgId),
                                                                    ('structure', 'rooted-hierarchy')])
            item = self._createNode(org, '', 'item', attrs=[('identifier', itemId)])
            return item
        return None

    def createResources(self, doc):
        manifest = doc.getElementsByTagName('manifest')
        if manifest:
            return self._createNode(manifest[0], '', 'resources')
        return None
                         
    def writeItem(self, orgs, itemId, refId, title):
        """ Write an item in the organizations section """
        itn = self._createNode(orgs, '', 'item', attrs=[('identifier', itemId),
                                                        ('identifierref', refId)])
        tn = self._createNode(itn, '', 'title', title)
        return tn

    def writeResource(self, res, refid, type, path):
        """ Write a resource object in the resources section """
        attrs = [('identifier', refid)]
        if type == 'Link':
            attrs.append(('type', 'imswl_xmlv1p0'))
        else:
            attrs.append(('type', 'webcontent'))
            attrs.append(('href', path))
        rn = self._createNode(res, '', 'resource', attrs=attrs)
        return rn

    def createResourceMetadata(self, res):
        """ Create a resource metadat node """
        md = self._createNode(res, '', 'metadata')
        return self._createNode(md, LOM_namespace, 'lom')
    
    def writeGeneralNode(self, lom, id, title, urlbase, lang, desc=None, kw=None):
        """ Write the general Node """
        gen = self._createNode(lom, '', 'general')
        idn = self._createNode(gen, '', 'identifier')
        self._createNode(idn, '', 'catalog', urlbase)
        self._createNode(idn, '', 'entry', id)
        tn = self._createNode(gen, '', 'title')
        self._createNode(tn, '', 'string', title, [('xml:lang', lang)])
        self._createNode(gen, '', 'language', lang)
        if desc:
            dn = self._createNode(gen, '', 'description')
            self._createNode(dn, '', 'string', desc, [('xml:lang', lang)])
        if kw:
            kn = self._createNode(gen, '', 'keyword')
            for k in kw:
                self._createNode(kn, '', 'string', k, [('xml:lang', lang)])

    def writeLifeCycleNode(self, lom, creators, contrib, mod, lang):
        """ Write the lifecycle Node """
        ln = self._createNode(lom, '', 'lifeCycle')
        if creators:
            self._createContributeElement(ln, '', LOM_version, 'author', creators, mod)
        if contrib:
            self._createContributeElement(ln, '', LOM_version, 'unknown', contrib, mod)

    def writeMetaMetadataNode(self, lom, id, urlbase, email, modtime, lang, contrib):
        """ write the metaMetadata Node """
        mmd = self._createNode(lom, '', 'metaMetadata')
        idn = self._createNode(mmd, '', 'identifier')
        if email:
            self._createNode(idn, '', 'catalog', '%s,%s' %(urlbase, email))
        else:
            self._createNode(idn, '', 'catalog', '%s' %urlbase)
        entry = self._createNode(idn, '', 'entry', id)
        if contrib:
            self._createContributeElement(mmd, '', LOM_version, 'creator', contrib, modtime)        
            self._createNode(mmd, '', 'metadataSchema', LOM_version)
        self._createNode(mmd, '', 'language', lang)

    def writeTechnicalNode(self, lom, format, size, location):
        """ Write the Technical Node """
        tech = self._createNode(lom, '', 'technical')
        self._createNode(tech, '', 'format', format)
        self._createNode(tech, '', 'size', size)
        self._createNode(tech, '', 'location', location)

    def writeRightsNode(self, lom, value, copyright, lang): 
        """ Write the Rights Node """
        rights = self._createNode(lom, '', 'rights')
        cwn = self._createNode(rights, '', 'copyrightAndOtherRestrictions')
        self._createNode(cwn, '', 'source', LOM_version)           
        self._createNode(cwn, '', 'value', value)
        if copyright:
            desc = self._createNode(rights, '', 'description')
            self._createNode(desc, '', 'string', copyright, [('xml:lang', lang)])


    def _createContributeElement(self, node,  ns, source, value, entities=[], date=None, email=None):
        """ writes out a Contribute Element """
        cn = self._createNode(node, ns, 'contribute')
        role = self._createNode(cn, '', 'role')
        self._createNode(role, '', 'source', source)
        self._createNode(role, '', 'value', value)
        if entities:
            if type(entities) not in [type([]), type(())]:
                entities = [entities]
            for e in entities:
                centity_node = self._createNode(cn, '', 'entity',self._createVCard(e,email))
        if date:
            dn = self._createNode(cn, '', 'date')
            self._createNode(dn, '', 'dateTime', date)

    def _createVCard(self, name, email=None):
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

    def writeResourceFile(self, res, path):
        """ Write a file node """
        self._createNode(res, '', 'file', attrs=[('href', path)])


    def getManifest(self, manifest):
        """ Get the manifest expressed in XML. """
        return manifest.toxml(encoding='utf-8')


    def _createNode(self, parent, nspace, ename, value=None, attrs=None):
        """ Create a node in the document. """
        newnode = self.document.createElementNS(nspace, ename)
        if nspace:
            newnode.setAttribute('xmlns', nspace)
        parent.appendChild(newnode)
        if value and value != '':
            if not isinstance(value, unicode):
                newnode.appendChild(self.document.createTextNode(value.decode('utf-8')))
            else:
                newnode.appendChild(self.document.createTextNode(value))
        if attrs:
            for x in attrs:
                newnode.setAttribute(x[0], x[1])
        return newnode

    def addNamespaces(self, manifest, namespaces):
        """ Add a namespace to the manifest. """
        for namespace in namespaces:
            manifest.setAttribute(namespace[0], namespace[1])

    def addSchemaLocations(self, manifest, schema_locations):
        manifest.setAttribute('xsi:schemaLocation', join(schema_locations, ' '))


    def getTextValue(self, node):
        """ Removes the text from the text_node of a node """
        for x in node.childNodes:
            if x.nodeType == x.TEXT_NODE:
                return x.nodeValue.strip()
        return None        

    def getLinkXml(self, title, link):
        """ Return text for a file that stores the link in an xml file """
        doc = minidom.Document()
        wlnode = self._createNode(doc, WL_namespace, 'webLink',
                                  attrs=[('xmlns:xsi', IMS_schemainst),('xmlns',WL_namespace)])
        self._createNode(wlnode, '', 'title', value=title)
        self._createNode(wlnode, '', 'url', attrs=[('href',link),('target','_blank')])
        return minidom.parseString(wlnode.toxml('utf-8')).toxml('utf-8')
