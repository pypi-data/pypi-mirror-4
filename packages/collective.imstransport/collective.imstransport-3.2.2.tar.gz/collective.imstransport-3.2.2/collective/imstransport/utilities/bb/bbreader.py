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
from urlparse import urlparse
from collective.imstransport.IMS_exceptions import ManifestError
from configbb import LOM_BB_namespace, XML_namespace, EMBEDDED_STRING
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from collective.imstransport.utilities.interfaces import IIMSTransportUtility
import re
import htmlentitydefs

class BBReader(object):

    def parseManifest(self, manifest):
        """ parse the manifest """
        return self.parseDataFile(manifest)

    def parseDataFile(self, dataxml):
        """ Parse the datafile """
        return minidom.parseString(dataxml)

    def readOrganizations(self, manifest):
        """ Read the organizations for the manifest """
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
                        title = self.getTextValue(titlenodes[0])
                        orgs[idref] =  title
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
                resource.getAttributeNS(LOM_BB_namespace, 'file'),
                resource.getAttributeNS(LOM_BB_namespace, 'title'),
                resource.getAttributeNS(XML_namespace, 'base'))

    def readFiles(self, resource, bbase):
        files = []
        flns = resource.getElementsByTagName('file')
        if flns:
            for fln in flns:
                file = fln.getAttribute('href')
                if bbase:
                    files.append('%s/%s' %(bbase, file))
                else:
                    files.append(file)
        return files

    def readMetadata(self, content):
        """ Read metadata from data files """
        md = {}
        self.readContentMetadata(content, md)
        return md

    def readContentMetadata(self, metadata, md):
        """ Read the metadata from a content file """
        content_nodes = metadata.getElementsByTagName('CONTENT')
        if content_nodes:
            content_node = content_nodes[0]
            title_nodes = content_node.getElementsByTagName('TITLE')        
            if title_nodes:
                title = title_nodes[0].getAttribute('value')
                md['title'] = self.runFilters(title,'striphtml')   
            body_nodes = content_node.getElementsByTagName('BODY')
            if body_nodes:
                text_nodes = body_nodes[0].getElementsByTagName('TEXT')
                if text_nodes:
                    text = self.getTextValue(text_nodes[0])
                    if text:
                        md['text'] = unquoteHTML(text)
            date_nodes = content_node.getElementsByTagName('DATES')
            if date_nodes:
                created_nodes = date_nodes[0].getElementsByTagName('CREATED')
                if created_nodes:
                    cdate = created_nodes[0].getAttribute('value')
                    cdateparts = cdate.split(' ')
                    if len(cdateparts) == 3:
                        creation_date = ' '.join(cdateparts[:-1])
                    else:
                        creation_date = ' '.join(cdateparts)
                    md['creation_date'] = creation_date
            flag_nodes = content_node.getElementsByTagName('FLAGS')
            if flag_nodes:
                isfolder_nodes = flag_nodes[0].getElementsByTagName('ISFOLDER')
                if isfolder_nodes:
                    value = isfolder_nodes[0].getAttribute('value')
                    if value ==  'true':
                        md['bbtype'] = 'Folder'
            handler_nodes = content_node.getElementsByTagName('CONTENTHANDLER')
            if handler_nodes:
                value = handler_nodes[0].getAttribute('value')
                if value == 'resource/x-bb-externallink':
                    url_nodes = content_node.getElementsByTagName('URL')
                    if url_nodes:
                        url = url_nodes[0].getAttribute('value') 
                        if url:
                            md['bbtype'] = 'Link'
                            md['remoteUrl'] = url        

    def readTocItem(self, manifest, resid):
        """ Read the toc page and find child nodes """
        tocitems = []
        organizations = manifest.getElementsByTagName('organizations')
        if organizations:
            organization_nodes = organizations[0].getElementsByTagName('organization')
            if organization_nodes:
                organization_node = organization_nodes[0]
                item_nodes = organization_nodes[0].getElementsByTagName('item')
                for item in item_nodes:
                    idref = item.getAttribute('identifierref')
                    if idref == resid:
                        childitems = item.childNodes
                        for x in childitems:
                            if x.nodeName == 'item':
                                itemid = x.getAttribute('identifierref')
                                tocitems.append(itemid)
        return tocitems


    def getDocumentHrefLinks(self, soup):
        links = []
        tags = soup.findAll(href=True)
        from urlparse import urlparse
        for tag in tags:
            if tag.has_key('href'):
                url = urlparse('href')
                if not url[1] or 'localhost' in url[1]:
                    links.append(tag)
        return links

    def getDocumentSrcLinks(self, soup):
        links = []
        tags = soup.findAll(src=True)
        from urlparse import urlparse
        for tag in tags:
            if tag.has_key('src'):
                url = urlparse('src')
                if not url[1] or 'localhost' in url[1]:
                    links.append(tag)
        return links

    def readEmbeddedTags(self, soup):
        """ Read embedded tags from a text file """
        prevlink = None
        links = self.getDocumentHrefLinks(soup)
        for link in links:
            if 'embedded' in link['href']:
                if prevlink and prevlink != link['href']:
                    return None
                prevlink = link['href']
        links = self.getDocumentSrcLinks(soup)
        for link in links:
            if 'embedded' in link['src']:
                if prevlink  and prevlink != link['src']:
                    return None
        return prevlink

    def createTocPage(self, entries):
        """ Create a table of links """
        text = '<table>'
        for z in entries:
            text += "<tr><td><a href='%s'>%s</a></td></tr>" %(z[0], z[1])
        text += '</table>'
        return text

    def _convertBBVariables(self, link, vars, base):
        """ Convert BB variables to their counterparts """
        lnk = link
        for var in vars:
            if base:
                replace = '%s/%s/' %(base, var[1])
            else:
                replace = var[1] + '/'
            lnk = link.replace(var[0], replace)
        return lnk

    def _convertURLEntities(self, link):
        """ Convert url entities """
        lnk = link
        import urllib
        lnk = urllib.unquote(lnk)
        return lnk

    def _convertToNormalizedLink(self, link, utils):
        """ Normalize the link so it can be imported without errors """
        lnk = link
        url = urlparse(lnk)
        urlfile = url[2].split('/')
        urlfile[-1] = utils.normalizeString(urlfile[-1])
        lnk = '/'.join(urlfile)
        return lnk
        
    def filterDocumentLink(self, link, utils, vars, base):
        lnk = link
        from urlparse import urlparse
        lnk = self._convertURLEntities(lnk)
        url = urlparse(lnk)
        if url[2] and not url[0]:
            lnk = self._convertBBVariables(lnk, vars, base)
            lnk = self._convertToNormalizedLink(lnk, utils)
        return lnk

    def runDocumentFilters(self, utils, soup, vars, base):
        """ Run a filter over the links """
        links = []
        links = self.getDocumentHrefLinks(soup)
        for link in links:
            orig = link['href']
            link['href'] = self.filterDocumentLink(link['href'], utils, vars, base)
        links = []
        links = self.getDocumentSrcLinks(soup)
        for link in links:
            orig = link['src']
            link['src'] = self.filterDocumentLink(link['src'], utils, vars, base)
        return soup.prettify()

    def runFilters(self, text, filters):
        """ Run filters over text """
        if 'striphtml' in filters:
            return self.stripHTML(text)

    def stripHTML(self, text):
        """ Remove all html tags and return the inner text """
        import re
        return re.sub('<([^!>]([^>]|\n)*)>','', text)

        
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
    if type(u'') == type(text):
        text = text.encode('utf-8')
    return re.sub(r'&(#?)(.+?);',convertHTMLEntity,text)
            
        
                
                
            

            
            
                



        
