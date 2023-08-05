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
from collective.imstransport.utilities.mit.mitreader import MITReader
from unittest import TestSuite, makeSuite
from xml.dom import minidom

organizations = """<organizations default="ocw_8-10Introduction-to-Electricity-TransformationsSpring2002">
    <organization identifier="ocw_8-10Introduction-to-Electricity-TransformationsSpring2002">
      <title>Introduction to Electricity Transformations</title>
      <item identifier="item00001" identifierref="res00001" ocw:sectionTemplateType="CourseHomePage" ocw:sectionTemplateVersion="2008-08-27">
        <title>Introduction to Electricity Transformations</title>
        <item identifier="item00002" identifierref="res00002" ocw:sectionTemplateType="GenericOther" ocw:sectionTemplateVersion="2008-11-24">
          <title>Sub-Section</title>
          <item identifier="item00003" identifierref="res00003">
            <title>8_10-2002-L02.pdf</title>
          </item>
        </item>
        <item identifier="item00004" identifierref="res00004">
          <title>Test Author Title</title>
        </item>
      </item>
      <item identifier="item00005" identifierref="res00005" ocw:sectionTemplateType="RepeatingBodyCopy" ocw:sectionTemplateVersion="2008-08-27">
        <title>Syllabus</title>
      </item>
    </organization>
  </organizations>
"""

resources = """<resources>
  <resource identifier="res00003" type="other" />
  <resource identifier="res00004" type="other" />
</resources>
"""

location = """<metadata>
  <adlcp:location>OcwWeb/Physics/8-10Intro-to-Electricity-TransformationsSpring2002/lecture5.pdf.xml</adlcp:location>
</metadata>
"""

general = """<lom:general uniqueElementName="general">
  <lom:title uniqueElementName="title">
    <lom:string language="en">Introduction to Electricity Transformations</lom:string>
  </lom:title>
  <lom:identifier>
    <lom:catalog uniqueElementName="catalog">OCW Master Course Number</lom:catalog>
    <lom:entry uniqueElementName="entry">8.10</lom:entry>
  </lom:identifier>
  <lom:language>en</lom:language>
  <lom:description>
    <lom:string language="en">Introductory course for Electricity Transformations</lom:string>
  </lom:description>
</lom:general>
"""

lifecycle = """
<lom:lifeCycle uniqueElementName="lifeCycle">
  <lom:version uniqueElementName="version">
    <lom:string language="en">Fall 2002</lom:string>
  </lom:version>
  <lom:contribute>
    <lom:role>
      <lom:source uniqueElementName="source">OCW_LOMv1.0</lom:source>
      <lom:value uniqueElementName="value">Author</lom:value>
    </lom:role>
    <lom:entity>Test Author</lom:entity>
    <lom:date uniqueElementName="date">
      <lom:dateTime uniqueElementName="dateTime">2008-08-27</lom:dateTime>
    </lom:date>
  </lom:contribute>
</lom:lifeCycle>
"""

pkglifecycle = """
<lom:lifecycle uniqueElementName="lifecycle">
  <lom:version uniqueElementName="version">
    <lom:string language="en">Fall 2002</lom:string>
  </lom:version>
  <lom:contribute>
    <lom:role>
      <lom:source uniqueElementName="source">OCW_LOMv1.0</lom:source>
      <lom:value uniqueElementName="value">Author</lom:value>
    </lom:role>
    <lom:entity>Test Author</lom:entity>
    <lom:date uniqueElementName="date">
      <lom:dateTime uniqueElementName="dateTime">2008-08-27</lom:dateTime>
    </lom:date>
  </lom:contribute>
</lom:lifecycle>
"""

technical = """<lom:technical>
  <lom:location>/test-folder/testexam2.jpg</lom:location>
  <lom:format>image/png</lom:format>
  <lom:size>124276</lom:size>
</lom:technical>
"""

rights = """<lom:rights>
    <lom:copyrightAndOtherRestrictions uniqueElementName="copyrightAndOtherRestrictions">
        <lom:source uniqueElementName="source">LOMv1.0</lom:source>
        <lom:value uniqueElementName="value">yes</lom:value>
    </lom:copyrightAndOtherRestrictions>
    <lom:cost>
        <lom:source uniqueElementName="source">LOMv1.0</lom:source>
        <lom:value uniqueElementName="value">no</lom:value>
    </lom:cost>
    <lom:description>
        <lom:string language="en">Test copyright message</lom:string>
    </lom:description>
</lom:rights>
"""

classification = """<lom:classification>
  <lom:taxonPath>
    <lom:source uniqueElementName="source">
      <lom:string language="en">CIP</lom:string>
    </lom:source>
    <lom:taxon>
      <lom:id uniqueElementName="id">400801</lom:id>
      <lom:entry uniqueElementName="entry">
        <lom:string language="en">Physics, General</lom:string>
      </lom:entry>
    </lom:taxon>
  </lom:taxonPath>
  <lom:keyword>
    <lom:string>
      test
    </lom:string>
  </lom:keyword>
  <lom:keyword>
    <lom:string>
      module
    </lom:string>
  </lom:keyword>
</lom:classification>
"""

mitbody = """
<html>
  <div id="content_body">
    Test content
  </div>
  <div>
    Test label
  </div>
</html>
"""

toplevel = general + pkglifecycle

LOM_namespace = 'http://ocw.mit.edu/xmlns/LOM'
OCW_namespace = 'http://ocw.mit.edu/xmlns/ocw_imscp'
ADLCP_namespace = 'http://www.adlnet.org/xsd/adlcp_rootv1p2'

class TestMITReader(IMSTransportTestCase):
    """
    """

    def testParseManifest(self):
        """ Test parsing of manifest node """
        mitr = MITReader()
        doc = mitr.parseManifest('<test>Hello</test>')
        assert(doc.getElementsByTagName('test'))

    def testReadPackageMetadata(self):
        """ Test the reading of package metadata """
        mitr = MITReader()
        pmd = {}
        manifest = '<manifest xmlns:lom="%s"><metadata>' %LOM_namespace + toplevel + '</metadata></manifest>'
        doc = mitr.parseManifest(manifest)
        pmd = mitr.readPackageMetadata(doc)
        assert(pmd.has_key('title'))
        self.assertEqual(pmd['title'], 'Introduction to Electricity Transformations')
        assert(pmd.has_key('language'))
        self.assertEqual(pmd['language'],'en')
        assert(pmd.has_key('description'))
        self.assertEqual(pmd['description'], 'Introductory course for Electricity Transformations')
        assert(pmd.has_key('creation_date'))
        self.assertEqual(pmd['creation_date'], '2008-08-27')
        assert(pmd.has_key('creators'))
        self.assertEqual(pmd['creators'], ['Test Author'])

    def testReadOrganizations(self):
        """ Test organization node handling """
        mitr = MITReader()
        manifest = '<manifest xmlns:ocw="%s"><metadata>' %OCW_namespace + organizations + '</metadata></manifest>'
        doc = minidom.parseString(manifest)
        orgs = mitr.readOrganizations(doc)
        assert(orgs)
        self.assertEqual(orgs['res00004'], (None, 'Test Author Title'))

    def testReadResources(self):
        """ Test resource node handling """
        mitr = MITReader()
        doc = minidom.parseString(resources)
        res = mitr.readResources(doc)
        assert(res)
        self.assertEqual(len(res), 2)

    def testGetTextValue(self):
        """ Test removal of text from node """
        document = minidom.parseString('<test>Hello</test>')
        textnode = document.getElementsByTagName('test')[0]
        mitr = MITReader()
        self.assertEqual(mitr.getTextValue(textnode), 'Hello')

    def testReadResourceAttributes(self):
        """ Test resource attributes handling """
        mitr = MITReader()
        doc = mitr.parseManifest(resources)
        res = doc.getElementsByTagName('resource')
        results = mitr.readResourceAttributes(res[0])
        self.assertEqual(results[0], 'res00003')
        self.assertEqual(results[1], 'other')
        self.assertEqual(results[2], '')

    def testReadLocation(self):
        """ Test the reading of location for data file """
        mitr = MITReader()
        manifest = '<manifest xmlns:adlcp="%s">' % ADLCP_namespace + location + '</manifest>'
        doc = mitr.parseManifest(manifest)
        loc = mitr.readLocation(doc)
        assert(loc)
        self.assertEqual(loc, 'OcwWeb/Physics/8-10Intro-to-Electricity-TransformationsSpring2002/lecture5.pdf.xml')

    def testReadGeneral(self):
        """ Test general node handling """
        mitr = MITReader()
        manifest = '<lom xmlns:lom="%s">' %LOM_namespace + general + '</lom>'
        doc = mitr.parseManifest(manifest)
        pmd = {}
        mitr.readGeneral(doc, pmd)
        assert(pmd.has_key('title'))
        self.assertEqual(pmd['title'], 'Introduction to Electricity Transformations')
        assert(pmd.has_key('language'))
        self.assertEqual(pmd['language'],'en')
        assert(pmd.has_key('description'))
        self.assertEqual(pmd['description'], 'Introductory course for Electricity Transformations')

    def testReadLifecycle(self):
        """ Test lifecycle node handling """
        mitr = MITReader()
        manifest = '<lom xmlns:lom="%s">' %LOM_namespace + lifecycle + '</lom>'
        doc = mitr.parseManifest(manifest)
        pmd = {}
        mitr.readLifecycle(doc, pmd)
        assert(pmd.has_key('creation_date'))
        self.assertEqual(pmd['creation_date'], '2008-08-27')
        assert(pmd.has_key('creators'))
        self.assertEqual(pmd['creators'], ['Test Author'])

    def testReadTechnical(self):
        """ Test technical node handling """
        mitr = MITReader()
        manifest = '<lom xmlns:lom="%s">' %LOM_namespace + technical + '</lom>'
        doc = mitr.parseManifest(manifest)
        pmd = {}
        mitr.readTechnical(doc, pmd)
        assert(pmd.has_key('Format'))
        self.assertEqual(pmd['Format'], 'image/png')

    def testReadRights(self):
        """ Test the reading of the rights node """
        mitr = MITReader()
        manifest = '<lom xmlns:lom="%s">' %LOM_namespace + rights + '</lom>'
        doc = mitr.parseManifest(manifest)
        pmd = {}
        mitr.readRights(doc, pmd)
        assert(pmd.has_key('rights'))
        self.assertEqual(pmd['rights'], 'Test copyright message')
        
    def testReadClassification(self):
        """ Test the reading of the classification node """
        mitr = MITReader()
        manifest = '<lom xmlns:lom="%s">' %LOM_namespace + classification + '</lom>'
        doc = mitr.parseManifest(manifest)
        pmd = {}
        mitr.readClassification(doc, pmd)
        assert(pmd.has_key('subject'))
        self.assertEqual(pmd['subject'], ['test','module'])
        
    def testRunFilters(self):
        """ Test the running of filters """
        mitr = MITReader()
        text = mitbody
        self.assertEqual(mitr.runFilters(mitbody,[]), text)
        self.assertNotEqual(mitr.runFilters(mitbody,['stripchrome']), text)

    def testRemoveMITChrome(self):
        """ Test the removing of MIT chrome elements """
        mitr = MITReader()
        text = mitbody
        self.assertEqual(mitr.runFilters(mitbody,['stripchrome']), '<div id="content_body">\nTest content\n</div>\n')        
        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestMITReader))
    return suite
