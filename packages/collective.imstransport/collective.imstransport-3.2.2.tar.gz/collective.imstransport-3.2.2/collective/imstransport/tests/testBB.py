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

from base import IMSTransportTestCase
from collective.imstransport.utilities.bb.bbreader import BBReader
from unittest import TestSuite, makeSuite
from xml.dom import minidom
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot

contentmetadata = """<CONTENT id="1000">
  <TITLE value="Test Folder"/>
  <BODY>
    <TEXT>Hello</TEXT>
    <TYPE value="H"/>
  </BODY>
  <DATES>
    <CREATED value="2007-01-04 15:53:25 EST"/>
    <UPDATED value="2007-01-04 15:53:25 EST"/>
    <START value=""/>
    <END value=""/>
  </DATES>
  <FLAGS>
    <ISFOLDER value="true"/>
  </FLAGS>
  <CONTENTHANDLER value="resource/x-bb-folder"/>
</CONTENT>
"""

organizations = """<organizations default="1000">
  <organization identifier="1000">
    <item identifier="itm2000" identifierref="res2000">
      <title>COURSE_DEFAULT.CourseInformation.CONTENT_LINK.label</title>
      <item identifier="itm3000" identifierref="res3000">
        <title>Test Document</title>
      </item>
      <item identifier="itm4000" identifierref="res4000">
        <title>Test File</title>
      </item>
      <item identifier="itm5000" identifierref="res5000">
        <title>Test Image</title>
      </item>
      <item identifier="itm6000" identifierref="res6000">
        <title>Test Folder</title>
        <item identifier="itm7000" identifierref="res7000">
          <title>Test Document 2</title>
        </item>
      </item>
    </item>
  </organization>
</organizations>
"""

resources = """<resources>
    <resource bb:file="res00001.dat" bb:title="COURSE_DEFAULT.CourseInformation.CONTENT_LINK.label" identifier="res00001" type="course/x-bb-coursetoc" xml:base="res00001"/>
    <resource bb:file="res00005.dat" bb:title="Test Document" identifier="res00005" type="resource/x-bb-document" xml:base="res00005"/>
    <resource bb:file="res00006.dat" bb:title="Test File" identifier="res00006" type="resource/x-bb-document" xml:base="res00006">
            <file href="embedded/samplefile.txt"/>
    </resource>
    <resource bb:file="res00007.dat" bb:title="Test Image" identifier="res00007" type="resource/x-bb-document" xml:base="res00007">
            <file href="embedded/!sampleimage.gif"/>
    </resource>
    <resource bb:file="res00002.dat" bb:title="COURSE_DEFAULT.CourseDocuments.CONTENT_LINK.label" identifier="res00002" type="course/x-bb-coursetoc" xml:base="res00002"/>
    <resource bb:file="res00010.dat" bb:title="Test Document" identifier="res00010" type="resource/x-bb-document" xml:base="res00010">
            <file href="course.html"/>
    </resource>
    <resource bb:file="res00003.dat" bb:title="COURSE_DEFAULT.Assignments.CONTENT_LINK.label" identifier="res00003" type="course/x-bb-coursetoc" xml:base="res00003"/>
    <resource bb:file="res00004.dat" bb:title="COURSE_DEFAULT.ExternalLinks.CONTENT_LINK.label" identifier="res00004" type="course/x-bb-coursetoc" xml:base="res00004"/>
</resources>
"""

hreflinks = """<div>
  <a href="http://www.plone.org">Plone</a>
  <a href="http://www.w3schools.com/html">w3c</a>
  <div>
    <link href="embedded/testdoc.html">Test Doc</link>
  </div>
</div>
"""

imglinks = """<div>
  <img src="http://plone.org/images/frontpage-image.png" /> 
  <iframe src="http://plone.org">
  <div>
    <img src="testimage.gif">Test Image</img>
  </div>
</div>
"""


BB_namespace = "http://www.blackboard.com/content-packaging/"
LOM_version = 'LOMv1.0'

class TestBBReader(IMSTransportTestCase):
    """
    """

    def testReadContentMetadata(self):
        """ Test the reading of content metadata """
        bbr = BBReader()
        data = contentmetadata
        doc = bbr.parseDataFile(data)
        pmd = {}
        bbr.readContentMetadata(doc, pmd)
        assert(pmd.has_key('title'))
        self.assertEqual(pmd['title'], 'Test Folder')
        assert(pmd.has_key('text'))
        self.assertEqual(pmd['text'], 'Hello')
        assert(pmd.has_key('creation_date'))
        self.assertEqual(pmd['creation_date'], '2007-01-04 15:53:25')
        assert(pmd.has_key('bbtype'))
        self.assertEqual(pmd['bbtype'], 'Folder')

    def testReadOrganizations(self):
        """ Test organization node handling """
        bbr = BBReader()
        doc = minidom.parseString(organizations)
        orgs = bbr.readOrganizations(doc)
        assert(orgs)
        self.assertEqual(len(orgs), 6)
        self.assertEqual(orgs['res7000'], 'Test Document 2')
        self.assertEqual(orgs['res3000'], 'Test Document')
        self.assertEqual(orgs['res6000'], 'Test Folder')
        self.assertEqual(orgs['res2000'], 'COURSE_DEFAULT.CourseInformation.CONTENT_LINK.label')
        self.assertEqual(orgs['res4000'], 'Test File')
        self.assertEqual(orgs['res5000'], 'Test Image')

    def testReadResources(self):
        """ Test resource node handling """
        bbr = BBReader()
        manifest = '<manifest xmlns:bb="%s">' % BB_namespace + resources + '</manifest>'
        doc = minidom.parseString(manifest)
        res = bbr.readResources(doc)
        self.assertEqual(len(res),8)

    def testGetTextValue(self):
        """ Test removal of text from node """
        document = minidom.parseString('<test>Hello</test>')
        textnode = document.getElementsByTagName('test')[0]
        bbr = BBReader()
        self.assertEqual(bbr.getTextValue(textnode), 'Hello')

    def testReadResourceAttributes(self):
        """ Test resource attributes handling """
        bbr = BBReader()
        manifest = '<manifest xmlns:bb="%s">' % BB_namespace + resources + '</manifest>'
        doc = bbr.parseManifest(manifest)
        res = doc.getElementsByTagName('resource')
        results = bbr.readResourceAttributes(res[0])
        self.assertEqual(results[0], 'res00001')
        self.assertEqual(results[1], 'course/x-bb-coursetoc')
        self.assertEqual(results[2], 'res00001.dat')
        self.assertEqual(results[3], 'COURSE_DEFAULT.CourseInformation.CONTENT_LINK.label')
        self.assertEqual(results[4], 'res00001')

    def testReadFiles(self):
        """ Testing the reading of files """
        bbr = BBReader()
        manifest = '<manifest xmlns:bb="%s">' % BB_namespace + resources + '</manifest>'
        doc = bbr.parseManifest(manifest)
        res = doc.getElementsByTagName('resource')        
        files = bbr.readFiles(res[2], 'res00006')
        self.assertEqual(files[0], 'res00006/embedded/samplefile.txt')
        files = bbr.readFiles(res[2], '')
        self.assertEqual(files[0], 'embedded/samplefile.txt')

    def testReadTocItem(self):
        """ Testing the reading of toc items """
        bbr = BBReader()
        doc = minidom.parseString(organizations)
        item = bbr.readTocItem(doc, 'res6000')
        self.assertEqual(item, ['res7000'])

    def testGetDocumentHrefLinks(self):
        """ Test the getting of href links """
        bbr = BBReader()
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(hreflinks)
        links = bbr.getDocumentHrefLinks(soup)
        assert(len(links), 3)
        self.assertEqual(str(links[0]), '<a href="http://www.plone.org">Plone</a>')

    def testGetDocumentSrcLinks(self):
        """ Test the getting of src links """
        bbr = BBReader()
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(imglinks)
        links = bbr.getDocumentSrcLinks(soup)
        assert(len(links), 3)
        self.assertEqual(str(links[0]), '<img src="http://plone.org/images/frontpage-image.png" />')

    def testReadEmbeddedTags(self):
        """ The the reading of embedded tags """
        bbr = BBReader()
        from BeautifulSoup import BeautifulSoup
        div = '<div>' + hreflinks + imglinks + '</div>'
        soup = BeautifulSoup(div)
        link = bbr.readEmbeddedTags(soup)
        self.assertEqual(link, 'embedded/testdoc.html')

    def testCreateTocPage(self):
        """ Test the creating of toc pages """
        bbr = BBReader()
        entries = [('http://www.plone.org', 'Plone'),
                   ('http://www.zope.org', 'Zope')]
        text = bbr.createTocPage(entries)
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(text)
        link = soup.findAll('a')
        self.assertEqual(link[0].get('href'), 'http://www.plone.org')

    def testConvertBBVariables(self):
        """ Test the conversion of Blackboard variables """
        bbr = BBReader()
        clink = bbr._convertBBVariables('@X@EmbeddedFile.location@X@testdoc.htm',[('@X@EmbeddedFile.location@X@', 'embedded')], 'res00006')
        self.assertEqual(clink, 'res00006/embedded/testdoc.htm')
        clink = bbr._convertBBVariables('@X@EmbeddedFile.location@X@testdoc.htm',[('@X@EmbeddedFile.location@X@', 'embedded')], None)
        self.assertEqual(clink, 'embedded/testdoc.htm')

    def testConvertURLEntities(self):
        """ Test the unquoting of url entities to their correct syntax """
        bbr = BBReader()
        clink = bbr._convertURLEntities('res0006/embedded/testdoc.htm%26name%3Dtest%20document')
        self.assertEqual('res0006/embedded/testdoc.htm&name=test document', clink)
    
    def testNormalizeString(self):
        """ Test the normalizing of strings """
        bbr = BBReader()
        utils = getUtility(ISiteRoot).plone_utils
        clink = bbr._convertToNormalizedLink('res00006/embedded/testdoc&name=test document', utils)
        self.assertEqual(clink, 'res00006/embedded/testdoc-name-test-document')

    def testFilterDocumentLink(self):
        """ Test the filtering of document content """
        bbr = BBReader()
        link = '@X@EmbeddedFile.location@X@testdoc.htm%26currlevel%3D50%26prev%3D23%26name%3Dtest%20name'
        utils = getUtility(ISiteRoot).plone_utils
        vars = [('@X@EmbeddedFile.location@X@', 'embedded')]
        base = 'res00006'
        clink = bbr.filterDocumentLink(link, utils, vars, base)        
        self.assertEqual(clink, 'res00006/embedded/testdoc-htm-currlevel-50-prev-23-name-test-name')
        link = 'http%3A//www.plone.org/testdoc.htm'
        clink = bbr.filterDocumentLink(link, utils, vars, base)        
        self.assertEqual(clink, 'http://www.plone.org/testdoc.htm')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestBBReader))
    return suite
