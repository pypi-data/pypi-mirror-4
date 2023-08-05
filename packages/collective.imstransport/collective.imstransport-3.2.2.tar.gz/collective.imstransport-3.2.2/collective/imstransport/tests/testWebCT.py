from base import IMSTransportTestCase
from collective.imstransport.utilities.webct.webctreader import WebCTReader
from unittest import TestSuite, makeSuite
from xml.dom import minidom


manifests = """<manifest>
  <manifest>
  </manifest>
  <manifest>
  </manifest>
  </manifest>
"""

toplevel = """<general>
      <title>
        <langstring xml:lang="en-US">WebCT Test Course</langstring>
      </title>
    </general>
    <educational>
      <learningresourcetype>
        <source>
          <langstring xml:lang="x-none">WebCT</langstring>
        </source>
        <value>
          <langstring xml:lang="x-none">Course</langstring>
        </value>
      </learningresourcetype>
    </educational>
"""

organizations = """<organizations default="1000">
  <organization identifier="1000">
    <item identifier="1002" identifierref="2000" isvisible="true">
      <title>Test Title 1</title>
    </item>
    <item identifier="1003" identifierref="2001" isvisible="true">
      <title>Test Title</title>
    </item>
  </organization>
</organizations>
"""

resources = """<resources>
  <resource identifier="2000" href="test.html" type="webcontent" />
</resources>
"""

resources2 = """<resources>
  <resource identifier="2000" type="webcontent" />
</resources>
"""

resources3 = """<resources>
  <resource identifier="2000" type="webcontent" />
  <resource identifier="3000" type="webcontent" />
  <resource identifier="4000" type="webcontent" />
</resources>
"""

general = """<general>
      <title>
        <langstring xml:lang="en-US">
          asdf
        </langstring>
      </title>
    </general>
"""

educational="""<educational>
  <learningresourcetype>
    <source>
      <langstring xml:lang="x-none">WebCT</langstring>
    </source>
    <value>
      <langstring xml:lang="x-none">Syllabus</langstring>
    </value>
  </learningresourcetype>
</educational>
"""

LOM_WEBCT_namespace = 'http://www.imsproject.org/metadata'
LOM_IMSCP_namespace = 'http://www.imsglobal.org/xsd/imsmd_v1p2'
LOM_version = 'LOMv1.0'

class TestWebCTReader(IMSTransportTestCase):
    """
    """

    def testParseManifest(self):
        """ Test parsing of manifest node """
        webctreader = WebCTReader()
        doc = webctreader.parseManifest('<test>Hello</test>')
        assert(doc.getElementsByTagName('test'))
        
    def testReadManifestsMetadata(self):
        """ Test the reading of top level manifests """
        webctreader = WebCTReader() 
        doc = minidom.parseString(manifests)
        mans = webctreader.readManifests(doc)
        self.assertEqual(len(mans), 3)

    def testReadPackageMetadata(self):
        """ Test the reading of package level metadata """
        webctreader = WebCTReader()
        manifest = '<metadata><lom xmlns="%s">' %LOM_WEBCT_namespace + toplevel + '</lom></metadata>'
        doc = webctreader.parseManifest(manifest)
        pmd = webctreader.readPackageMetadata(doc)
        assert(pmd.has_key('title'))
        self.assertEqual(pmd['title'], 'WebCT Test Course')
        assert(pmd.has_key('webcttype'))
        self.assertEqual(pmd['webcttype'], 'Course')

    def testReadOrganizations(self):
        """ Test organization node handling """
        webctreader = WebCTReader()
        manifest = '<manifest>' + organizations + '</manifest>'
        doc = webctreader.parseManifest(manifest)
        orgs = webctreader.readOrganizations(doc)
        assert(orgs.has_key('2000'))
        self.assertEqual(orgs['2000'], 'Test Title 1')
        self.assertEqual(len(orgs), 2)

    def readResources(self):
        """ Test the resource node handling """
        webctreader = WebCTReader()
        manifest = '<manifest>' + resources3 + '</manifest>'
        doc = webctreader.parseManifest(manifest)
        res = webctreader.readResources(doc)
        assert(res)
        self.assertEqual(len(res), 3)

    def testGetTextValue(self):
        """ Test removal of test from node """
        document = minidom.parseString('<test>Hello</test>')
        textnode = document.getElementsByTagName('test')[0]
        webctreader = WebCTReader()
        self.assertEqual(webctreader.getTextValue(textnode), 'Hello')      

    def readResourcesAttributes(self):
        """ Test resource attributes node handling """
        webctreader = WebCTReader()
        manifest = '<manifest>' + resources + '</manifest>'
        doc = webctreader.parseManifest(manifest)
        res = webctreader.readResources(doc)
        assert(res)
        id, type, href = webctreader.readResourceAttributes(res[0])
        self.assertEqual('2000', id)
        self.assertEqual('test.html', href)
        self.assertEqual('webcontent', type)
        manifest = '<manifest>' + resources2 + '</manifest>'
        doc = webctreader.parseManifest(manifest)
        res = webctreader.readResources(doc)
        assert(res)
        id, type, href = webctreader.readResourceAttributes(res[0])        
        self.assertEqual('2000', id)
        self.assertEqual(None, href)
        self.assertEqual('webcontent', type)

    def testReadGeneral(self):
        """ Test general node handling """
        webctreader = WebCTReader()
        manifest = '<metadata><lom xmlns="%s">' %LOM_WEBCT_namespace + general + '</lom></metadata>'
        doc = webctreader.parseManifest(manifest)
        pmd = {}
        gen = webctreader.readGeneral(doc, pmd)
        self.assertEqual(pmd['title'],'asdf')

    def testReadEducational(self):
        """ Test educational node handling """
        webctreader = WebCTReader()
        manifest = '<metadata><lom xmlns="%s">' %LOM_WEBCT_namespace + educational + '</lom></metadata>'
        doc = webctreader.parseManifest(manifest)
        pmd = {}
        edu = webctreader.readEducational(doc, pmd)
        self.assertEqual(pmd['webcttype'],'Syllabus')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestWebCTReader))
    return suite
