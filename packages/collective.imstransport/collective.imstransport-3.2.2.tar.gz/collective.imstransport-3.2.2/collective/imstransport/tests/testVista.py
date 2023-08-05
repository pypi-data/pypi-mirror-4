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
from collective.imstransport.utilities.webctvista.webctvistareader import WebCTVistaReader
from unittest import TestSuite, makeSuite
from xml.dom import minidom

organizations = """
<organizations>
    <organization identifier="val00002_O" structure="webct:VistaLearningModule">
        <item identifier="val00002_I1" identifierref="res00002_1" isvisible="true" xsi:type="webctlm:LearningModuleItemType" webctlm:coType="webct.page">
            <title>Test Title 1</title>
            <item identifier="val00002_I2" identifierref="res00002_2" isvisible="true" xsi:type="webctlm:LearningModuleItemType" webctlm:coType="webct.page">
                <title>Test Title 2</title>
                <webctlm:ActionMenu/>
            </item>
            <webctlm:ActionMenu webctlm:bookmarks="false" webctlm:notes="false" webctlm:compile="true"/>
        </item>
    </organization>
</organizations>
"""

resources = """
<resources>
    <resource identifier="res00002_1" type="webct.manifest" webct:coType="webct.page" xsi:type="webct:ResourceType">
        <file href="test-folder/473849.xml"/>
    </resource>
    <resource identifier="res00002_2" type="webct.manifest" webct:coType="webct.page" xsi:type="webct:ResourceType">
        <file href="test-folder/808490.xml "/>
    </resource>
</resources>
"""

general = """<imsmd:general>
    <imsmd:title>
        <imsmd:langstring xml:lang="en-US">test-image.jpg</imsmd:langstring>
    </imsmd:title>
</imsmd:general>
"""

educational = """<imsmd:educational>
    <imsmd:learningresourcetype>
        <imsmd:source>
            <imsmd:langstring xml:lang="x-none">WebCT</imsmd:langstring>
        </imsmd:source>
        <imsmd:value>
            <imsmd:langstring xml:lang="x-none">webct.file</imsmd:langstring>
        </imsmd:value>
    </imsmd:learningresourcetype>
</imsmd:educational>
"""

content = """<webct:ContentObject webct:coType="webct.file" xsi:type="webctfl:FileType">
    <webct:Name>test-image.jpg</webct:Name>
    <webctfl:CharacterSet>utf-8</webctfl:CharacterSet>
    <webctfl:Path>test-folder\images</webctfl:Path>
</webct:ContentObject>
"""

LOM_IMSCP_namespace = 'http://www.imsglobal.org/xsd/imsmd_v1p2'
LOM_version = 'LOMv1.0'
LOM_WEBCT_namespace = "http://www.imsglobal.org/xsd/imsmd_v1p2"
XSI_namespace = 'http://www.w3.org/2001/XMLSchema-instance'
WEBCT_namespace = 'http://www.webct.com/xsd/cisv3'
WEBCT_FILE_namespace = 'http://www.webct.com/xsd/cisfilev3'

class TestWebCTVistaReader(IMSTransportTestCase):
    """
    """
    
    def testParseManifest(self):
        """ Test parsing of manifest node """
        wctr = WebCTVistaReader()
        doc = wctr.parseManifest('<test>Hello</test>')
        assert(doc.getElementsByTagName('test'))

    def testReadOrganizations(self):
        """ Test organization node handling """
        wctr = WebCTVistaReader()
        manifest = '<manifest xmlns:xsi="%s" xmlns:webct="%s" xmlns:webctlm="%s">' %(XSI_namespace, LOM_WEBCT_namespace, WEBCT_namespace) + organizations + '</manifest>'
        doc = minidom.parseString(manifest)
        orgs = wctr.readOrganizations(doc)
        assert(orgs)
        self.assertEqual(len(orgs), 2)
        self.assertEqual(orgs['res00002_1'], 'Test Title 1')
        self.assertEqual(orgs['res00002_2'], 'Test Title 2')

    def testReadResources(self):
        """ Test resource node handling """
        wctr = WebCTVistaReader()
        manifest = '<manifest xmlns:xsi="%s" xmlns:webct="%s">' %(XSI_namespace, LOM_WEBCT_namespace) + resources + '</manifest>'
        doc = minidom.parseString(manifest)
        res = wctr.readResources(doc)
        assert(res)
        self.assertEqual(len(res),2)

    def testGetTextValue(self):
        """ Test removal of text from node """
        document = minidom.parseString('<test>Hello</test>')
        textnode = document.getElementsByTagName('test')[0]
        wctr = WebCTVistaReader()
        self.assertEqual(wctr.getTextValue(textnode), 'Hello')

    def testReadResourceAttributes(self):
        """ Test resource attributes handling """
        wctr = WebCTVistaReader()
        manifest = '<manifest xmlns:xsi="%s" xmlns:webct="%s">' %(XSI_namespace, LOM_WEBCT_namespace) + resources + '</manifest>'
        doc = wctr.parseManifest(manifest)
        res = doc.getElementsByTagName('resource')
        results = wctr.readResourceAttributes(res[0])
        self.assertEqual(results[0], 'res00002_1')
        self.assertEqual(results[1], 'webct.manifest')
        self.assertEqual(results[2], '')

    def testReadMetadata(self):
        pass

    def testReadGeneral(self):
        """ Test general node handling """
        wctr = WebCTVistaReader()
        manifest = '<imsmd:lom xmlns:imsmd="%s">' %LOM_WEBCT_namespace + general + '</imsmd:lom>'
        doc = wctr.parseManifest(manifest)
        md = {}
        wctr.readGeneral(doc, md)
        assert(md.has_key('title'))
        self.assertEqual(md['title'], 'test-image.jpg')

    def testReadEducational(self):
        """ Test educational node handling """
        wctr = WebCTVistaReader()
        manifest = '<imsmd:lom xmlns:imsmd="%s">' %LOM_WEBCT_namespace + educational + '</imsmd:lom>'
        doc = wctr.parseManifest(manifest)
        md = {}
        wctr.readEducational(doc, md)
        assert(md.has_key('webcttype'))
        self.assertEqual(md['webcttype'], 'webct.file')

    def testReadFiles(self):
        """ Test the reading of files """
        wctr = WebCTVistaReader()
        manifest = '<manifest xmlns:xsi="%s" xmlns:webct="%s">' %(XSI_namespace, LOM_WEBCT_namespace) + resources + '</manifest>'
        doc = minidom.parseString(manifest)
        res = wctr.readResources(doc)
        fl = wctr.readFiles(res[0])
        assert(fl)
        self.assertEqual(fl[0],'test-folder/473849.xml')

    def testReadContentMetadata(self):
        """ Test the reading of content metadata """
        wctr = WebCTVistaReader()
        manifest = '<manifest xmlns:xsi="%s" xmlns:webct="%s" xmlns:webctfl="%s">' %(XSI_namespace, WEBCT_namespace, WEBCT_FILE_namespace) + content + '</manifest>'
        doc = minidom.parseString(manifest)
        pmd = {}
        wctr.readContentMetadata(doc,pmd)
        assert(pmd)
        self.assertEqual(pmd['id'],'test-image.jpg')
        self.assertEqual(pmd['path'],'test-folder/images')
        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestWebCTVistaReader))
    return suite
