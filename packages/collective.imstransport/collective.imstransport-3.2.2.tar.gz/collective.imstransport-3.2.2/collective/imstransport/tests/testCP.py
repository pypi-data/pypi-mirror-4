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
from collective.imstransport.utilities.imscp.cpreader import CPReader
from collective.imstransport.utilities.imscp.cpwriter import CPWriter
from unittest import TestSuite, makeSuite
from xml.dom import minidom

toplevel = """<general>
      <identifier>
        asdf
      </identifier>
      <title>
        <langstring xml:lang="en">
          test module
        </langstring>
      </title>
      <language>
        en
      </language>
      <description>
        <langstring xml:lang="en">
          This is a test module
        </langstring>
      </description>
      <keyword>
        <langstring xml:lang="en">
          test
        </langstring>
        <langstring xml:lang="en">
          module
        </langstring>
        <langstring xml:lang="en">
          educational
        </langstring>
      </keyword>
    </general>
"""

organizations = """<organizations default="1000">
  <organization identifier="1000">
    <item identifier="1002" identifierref="2000">
      <title>Test Title 1</title>
    </item>
    <item identifier="1003" identifierref="2001">
      <title>Test Title</title>
    </item>
  </organization>
</organizations>
"""

resources = """<resources>
  <resource identifier="2000" href="test.html" type="webcontent" />
</resources>
"""

general = """<general>
      <identifier>
        asdf
      </identifier>
      <title>
        <langstring xml:lang="en">
          asdf
        </langstring>
      </title>
      <language>
        en
      </language>
      <description>
        <langstring xml:lang="en">
          this is a test
        </langstring>
      </description>
      <keyword>
        <langstring xml:lang="en">
          Hello
        </langstring>
        <langstring xml:lang="en">
          There
        </langstring>
      </keyword>
    </general>
"""

lifecycle = """<lifecycle>
  <contribute>
    <role>
      <source>
        <langstring xml:lang="x-none">
          LOMv1.0
        </langstring>
      </source>
      <value>
        <langstring xml:lang="x-none">
          author
        </langstring>
      </value>
    </role>
    <centity>
      <vcard>
        BEGIN:VCARD
        FN: Sandra Suzannah Serendipity
        END:VCARD
      </vcard>
    </centity>
    <centity>
      <vcard>
        BEGIN:VCARD 
        FN:HUGO 
        END:VCARD
      </vcard>
    </centity>
    <centity>
      <vcard> 
        BEGIN:VCARD
        FN: Quincy Adams
        END:VCARD
      </vcard>
    </centity>
    <date>
      <datetime>
        2009-05-09 15:07:16
      </datetime>
    </date>
  </contribute>
  <contribute>
    <role>
      <source>
        <langstring xml:lang="x-none">
          LOMv1.0
        </langstring>
      </source>
      <value>
        <langstring xml:lang="x-none">
          unknown
        </langstring>
      </value>
    </role>
    <centity>
      <vcard>
        BEGIN:VCARD
        FN:Garth
        END:VCARD
      </vcard>
    </centity>
    <date>
      <datetime>
        2009-05-11 15:07:16
      </datetime>
    </date>
  </contribute>
</lifecycle>
"""

technical = """<technical>
  <format>
    image/png
  </format>
</technical>
"""

rights = """<rights>
  <copyrightandotherrestrictions>
    <source>
      <langstring xml:lang="x-none">
        LOMv1.0
      </langstring>
    </source>
      <value>
        <langstring xml:lang="x-none">
          yes
        </langstring>
      </value>
   </copyrightandotherrestrictions>
   <description>
     <langstring xml:lang="x-none">
       This material is copyrighted.
     </langstring>
   </description>
</rights>
"""

entity="""<centity>
  <vcard>
    BEGIN:VCARD
    FN:  Harrison Cheever
    EMAIL;INTERNET: harrc@plone.org
    END:VCARD
  </vcard>
</centity>
"""

LOM_IMSCP_namespace = 'http://www.imsglobal.org/xsd/imsmd_v1p2'
LOM_version = 'LOMv1.0'

class TestCPReader(IMSTransportTestCase):
    """
    """

    def testParseManifest(self):
        """ Test parsing of manifest node """
        cpr = CPReader()
        doc = cpr.parseManifest('<test>Hello</test>')
        assert(doc.getElementsByTagName('test'))

    def testReadPackageMetadata(self):
        """ Test the reading of package level metadata """
        cpr = CPReader()
        manifest = '<metadata><lom xmlns="%s">' %LOM_IMSCP_namespace + toplevel + '</lom></metadata>'
        doc = cpr.parseManifest(manifest)
        pmd = cpr.readPackageMetadata(doc)
        assert(pmd.has_key('title'))
        self.assertEqual(pmd['title'], 'test module')
        assert(pmd.has_key('language'))
        self.assertEqual(pmd['language'], 'en')
        assert(pmd.has_key('description'))
        self.assertEqual(pmd['description'], 'This is a test module')
        assert(pmd.has_key('subject'))
        self.assertEqual(pmd['subject'], ['test', 'module', 'educational'])

    def testReadOrganizations(self):
        """ Test organization node handling """
        cpr = CPReader()
        doc = minidom.parseString(organizations)
        orgs = cpr.readOrganizations(doc)
        assert(orgs)
        self.assertEqual(len(orgs), 2)
        self.assertEqual(orgs['2000'], (1, 'Test Title 1'))
        self.assertEqual(orgs['2001'], (2, 'Test Title'))

    def testReadResources(self):
        """ Test resource node handling """
        cpr = CPReader()
        doc = minidom.parseString(resources)
        res = cpr.readResources(doc)
        assert(res)
        self.assertEqual('2000', res[0].getAttribute('identifier'))
        self.assertEqual('test.html', res[0].getAttribute('href'))
        self.assertEqual('webcontent', res[0].getAttribute('type'))

    def testGetTextValue(self):
        """ Test removal of text from node """
        document = minidom.parseString('<test>Hello</test>')
        textnode = document.getElementsByTagName('test')[0]
        cpr = CPReader()
        self.assertEqual(cpr.getTextValue(textnode), 'Hello')

    def testReadResourceAttributes(self):
        """ Test resource attributes handling """
        cpr = CPReader()
        doc = cpr.parseManifest(resources)
        res = doc.getElementsByTagName('resource')
        results = cpr.readResourceAttributes(res[0])
        self.assertEqual(results[0], '2000')
        self.assertEqual(results[1], 'webcontent')
        self.assertEqual(results[2], 'test.html')

    def testReadMetadata(self):
        pass

    def testReadGeneral(self):
        """ Test general node handling """
        cpr = CPReader()
        manifest = '<lom xmlns="%s">' %LOM_IMSCP_namespace + general + '</lom>'
        doc = cpr.parseManifest(manifest)
        md = {}
        cpr.readGeneral(doc, md)
        assert(md.has_key('title'))
        self.assertEqual(md['title'], 'asdf')
        assert(md.has_key('language'))
        self.assertEqual(md['language'], 'en')
        assert(md.has_key('description'))
        self.assertEqual(md['description'], 'this is a test')
        assert(md.has_key('subject'))
        self.assertEqual(md['subject'], ['Hello', 'There'])

    def testReadLifecycle(self):
        """ Test lifecycle node handling """
        cpr = CPReader()
        manifest = '<lom xmlns="%s">' %LOM_IMSCP_namespace + lifecycle + '</lom>'
        doc = cpr.parseManifest(manifest)
        md = {}
        cpr.readLifecycle(doc, md)
        assert(md.has_key('creators'))
        self.assertEqual(md['creators'], ['Sandra Suzannah Serendipity','HUGO','Quincy Adams'])
        assert(md.has_key('contributors'))
        self.assertEqual(md['contributors'], ['Garth'])
        assert(md.has_key('creation_date'))
        self.assertEqual(md['creation_date'], '2009-05-09 15:07:16')

    def testTechnical(self):
        """ Test technical node handling """
        cpr = CPReader()
        manifest = '<lom xmlns="%s">' %LOM_IMSCP_namespace + technical + '</lom>'
        doc = cpr.parseManifest(manifest)
        md = {}
        cpr.readTechnical(doc, md)
        assert(md.has_key('Format'))
        self.assertEqual(md['Format'], 'image/png')

    def testReadRights(self):
        """ Test rights node handling """
        cpr = CPReader()
        manifest = '<lom xmlns="%s">' %LOM_IMSCP_namespace + rights + '</lom>'
        doc = cpr.parseManifest(manifest)
        md = {}
        cpr.readRights(doc, md)
        assert(md.has_key('rights'))
        self.assertEqual(md['rights'],'This material is copyrighted.')

    def testVcardValues(self):
        """ Testing reading VCards Sections """
        cpr = CPReader()
        manifest = '<lom xmlns="%s">' %LOM_IMSCP_namespace + entity + '</lom>'
        doc = cpr.parseManifest(manifest)
        md = {}
        entity_nodes = doc.getElementsByTagName('centity')
        vcard_nodes = entity_nodes[0].getElementsByTagName('vcard')
        name, email = cpr.getVcardValues(vcard_nodes[0])
        self.assertEqual(name, 'Harrison Cheever')
        self.assertEqual(email, 'harrc@plone.org')

    def testVcardValue(self):
        """ Test reading of VCard line """
        cpr = CPReader()
        text = '\n  FN:    Howard Maggleby \n '
        val = cpr.getVcardValue('FN', text.split('\n'))
        self.assertEqual(val, 'Howard Maggleby')

class TestCPWriter(IMSTransportTestCase):
    """
    """
    
    def testWriteManifest(self):
        """ Test for writing of manifest """
        cpw = CPWriter()
        doc = cpw.createManifest('001', '2009-05-12 15:07:34')
        man = doc.getElementsByTagName('manifest')
        id = man[0].getAttribute('identifier')
        ver = man[0].getAttribute('xmlns:version')
        self.assertEqual(id, '001')
        self.assertEqual(ver, '2009-05-12 15:07:34')

    def testTopLevelMeta(self):
        """ Test for writing of top level metadata """
        cpw = CPWriter()
        doc = cpw.createManifest('001', '2009-05-12 15:07:34')
	cpw.writeTopLevelMetadata(doc, '001', 'Test Module', 'http://plone.org', 'en', 'This is a test module', ['test','module','educational'])
        man = doc.getElementsByTagName('manifest')
        md = man[0].getElementsByTagName('metadata')
        sch = md[0].getElementsByTagName('schema') 
        ver = md[0].getElementsByTagName('schemaversion')
        lom = md[0].getElementsByTagNameNS(LOM_IMSCP_namespace, 'lom')
        gen = lom[0].getElementsByTagName('general')
        ident = gen[0].getElementsByTagName('identifier')
        tn = gen[0].getElementsByTagName('title')
        tnstr = tn[0].getElementsByTagName('langstring')
        lang = gen[0].getElementsByTagName('language')
        dn = gen[0].getElementsByTagName('description')
        dnstr = dn[0].getElementsByTagName('langstring')
        kn = gen[0].getElementsByTagName('keyword')
        knstrs = kn[0].getElementsByTagName('langstring')
        kws = [kw.childNodes[0].nodeValue for kw in knstrs]
        schval = sch[0].childNodes[0].nodeValue
        verval = ver[0].childNodes[0].nodeValue
        identval = ident[0].childNodes[0].nodeValue
        tnstrval = tnstr[0].childNodes[0].nodeValue
        langval = lang[0].childNodes[0].nodeValue
        dnstrval = dnstr[0].childNodes[0].nodeValue
        self.assertEqual(schval, 'IMS Content Package')
        self.assertEqual(verval, '1.2')
        self.assertEqual(identval, '001')
        self.assertEqual(tnstrval, 'Test Module')
        self.assertEqual(langval, 'en')
        self.assertEqual(dnstrval, 'This is a test module')
        self.assertEqual(kws, ['test', 'module', 'educational'])

    def testCreateOrganizations(self):
        """ Test for writing of organizations, organization, and shell item elements """
        cpw = CPWriter()
        doc = cpw.createManifest('001', '2009-05-12 15:07:34')
        man = doc.getElementsByTagName('manifest')
        cpw.createOrganizations(doc, 'org001')
        man = doc.getElementsByTagName('manifest')
        orgs = man[0].getElementsByTagName('organizations')
        org = orgs[0].getElementsByTagName('organization')
        orgid = org[0].getAttribute('identifier')
        default = orgs[0].getAttribute('default')
        self.assertEqual(orgid, 'org001')
        self.assertEqual(default, 'org001')

    def testCreateResources(self):
        """ Test for writing of resources element """
        cpw = CPWriter()
    	doc = cpw.createManifest('001', '2009-05-12 15:07:34')
        cpw.createResources(doc)
        man = doc.getElementsByTagName('manifest')
        resources = man[0].getElementsByTagName('resources')
        assert(resources)
        
    def testWriteItem(self):
        """ Test for writing of a single element """
        cpw = CPWriter()
    	doc = cpw.createManifest('001', '2009-05-12 15:07:34')
        cpw.createOrganizations(doc, 'org001')
        orgs = doc.getElementsByTagName('organizations')
        title = cpw.writeItem(orgs[0], 'item001', 'res001', 'This is a test item')
        itn = orgs[0].getElementsByTagName('item')
        # Get the last item added and verify attributes
        itemid = itn[-1].getAttribute('identifier')
        refid = itn[-1].getAttribute('identifierref')
        isvis = itn[-1].getAttribute('isvisible')
        tnstr = title.childNodes[0].nodeValue
        self.assertEqual(itemid, 'item001')
        self.assertEqual(refid, 'res001')
        self.assertEqual(isvis, 'true')
        self.assertEqual(tnstr, 'This is a test item')

    def testWriteResource(self):
        """ Test for single of resource element """
        cpw = CPWriter()
    	doc = cpw.createManifest('001', '2009-05-12 15:07:34')
        res = cpw.createResources(doc)
        rn1 = cpw.writeResource(res, 'res002', 'File', 'test-module/test.gif')
        rn2 = cpw.writeResource(res, 'res003', 'Document', 'test-module/index.html')
        idval1 = rn1.getAttribute('identifier')
        typeval1 = rn1.getAttribute('type')
        hrefval1 = rn1.getAttribute('href')        
        idval2 = rn2.getAttribute('identifier')
        typeval2 =  rn2.getAttribute('type')
        hrefval2 = rn2.getAttribute('href')
        self.assertEqual(idval1, 'res002')
        self.assertEqual(typeval1, 'webcontent')
        self.assertEqual(hrefval1, 'test-module/test.gif')
        self.assertEqual(idval2, 'res003')
        self.assertEqual(typeval2, 'webcontent')
        self.assertEqual(hrefval2, 'test-module/index.html')

    def testCreateResourceMetadata(self):
        """ Test for writing of resource metadata """
        cpw = CPWriter()
    	doc = cpw.createManifest('001', '2009-05-12 15:07:34')
        res = cpw.createResources(doc)
        res = cpw.createResources(doc)
        rn = cpw.writeResource(res, 'res001', 'Document', 'test-module/test-doc.html')
        cpw.createResourceMetadata(rn)
        mdn = rn.getElementsByTagName('metadata')
        lom = mdn[0].getElementsByTagNameNS(LOM_IMSCP_namespace, 'lom')
        assert(lom)

    def testWriteGeneralNode(self):
        """ Test for writing of general node """
        cpw = CPWriter()
        lom = minidom.Document()
        cpw.writeGeneralNode(lom, 'res001', 'Resource 001', 'en', 'Test item number 001', ['test', 'module', 'educational'])
        gen = lom.getElementsByTagName('general')
        idn = gen[0].getElementsByTagName('identifier')
        tn = gen[0].getElementsByTagName('title')
        tnstr = tn[0].getElementsByTagName('langstring')
        lang = gen[0].getElementsByTagName('language')
        dn = gen[0].getElementsByTagName('description')
        dnstr = dn[0].getElementsByTagName('langstring')
        kn = gen[0].getElementsByTagName('keyword')
        knstrs = kn[0].getElementsByTagName('langstring')
        kws = [kw.childNodes[0].nodeValue for kw in knstrs]
        idnval = idn[0].childNodes[0].nodeValue
        tnstrval = tnstr[0].childNodes[0].nodeValue
        langval = lang[0].childNodes[0].nodeValue
        dnstrval = dnstr[0].childNodes[0].nodeValue
        self.assertEqual(idnval,'res001')
        self.assertEqual(tnstrval,'Resource 001')
        self.assertEqual(langval,'en')
        self.assertEqual(dnstrval,'Test item number 001')
        self.assertEqual(kws,['test', 'module', 'educational'])

    def testWriteLifeCycleNode(self):
        """ Test for writing life cycle node """
        cpw = CPWriter()
        lom = minidom.Document()
        cpw.writeLifeCycleNode(lom, ['test-creator1', 'Test creator2'], ['test-contributor1', 'Test Contributor2'], '2009-05-12 15:07:34', 'en')
        ln = lom.getElementsByTagName('lifecycle')
        an = ln[0].getElementsByTagName('contribute')
        assert(ln)
        self.assertEqual(len(an), 2)

    def testWriteMetaMetadataNode(self):
        """ Test for writing metaMetadata node """
        cpw = CPWriter()
        lom = minidom.Document()        
        cpw.writeMetaMetadataNode(lom, 'res001', 'http://www.enpraxis.net', 'user@enpraxis.net', '2009-05-12 15:07:34', 'en', ['test-contributor1', 'Test Contributor2'])
        mmdn = lom.getElementsByTagName('metametadata')
        idn = mmdn[0].getElementsByTagName('catalogentry')
        cat = idn[0].getElementsByTagName('catalog')
        entn = idn[0].getElementsByTagName('entry')
        ent = entn[0].getElementsByTagName('langstring')
        mdsc = mmdn[0].getElementsByTagName('metadatascheme')       
        lang = mmdn[0].getElementsByTagName('language')
        catval = cat[0].childNodes[0].nodeValue
        entval = ent[0].childNodes[0].nodeValue
        mdscval = mdsc[0].childNodes[0].nodeValue
        langval = lang[0].childNodes[0].nodeValue
        self.assertEqual(catval, 'http://www.enpraxis.net,user@enpraxis.net')
        self.assertEqual(entval, 'res001')
        self.assertEqual(mdscval, 'LOMv1.0')
        self.assertEqual(langval, 'en')

    def testWriteTechnicalNode(self):
        """ Test for writing of technical node """
        cpw = CPWriter()
        lom = minidom.Document()
        cpw.writeTechnicalNode(lom, 'text/html', '22', 'http://enpraxis.net/course/test-file.html')
        techn = lom.getElementsByTagName('technical')
        fmn = techn[0].getElementsByTagName('format')
        sn = techn[0].getElementsByTagName('size')
        lcn = techn[0].getElementsByTagName('location')
        fmnval = fmn[0].childNodes[0].nodeValue
        snval = sn[0].childNodes[0].nodeValue
        lcnval = lcn[0].childNodes[0].nodeValue
        self.assertEqual(fmnval, 'text/html')
        self.assertEqual(snval, '22')
        self.assertEqual(lcnval, 'http://enpraxis.net/course/test-file.html')

    def testWriteRightsNode(self):
        """ Test for writing of rights node """
        cpw = CPWriter()
        lom = minidom.Document()
        cpw.writeRightsNode(lom, 'yes', 'Description of test document 001', 'en')
        rights = lom.getElementsByTagName('rights')
        crn = rights[0].getElementsByTagName('copyrightandotherrestrictions')
        sn_node = crn[0].getElementsByTagName('source')
        sn = sn_node[0].getElementsByTagName('langstring')        
        val_node = crn[0].getElementsByTagName('value')
        val = val_node[0].getElementsByTagName('langstring')
        dn = rights[0].getElementsByTagName('description')
        dnstr = dn[0].getElementsByTagName('langstring')
        lang = dnstr[0].getAttribute('xml:lang')
        snval = sn[0].childNodes[0].nodeValue
        valval = val[0].childNodes[0].nodeValue
        dnstrval = dnstr[0].childNodes[0].nodeValue
        self.assertEqual(snval, 'LOMv1.0')
        self.assertEqual(valval, 'yes')
        self.assertEqual(dnstrval, 'Description of test document 001')
        self.assertEqual(lang, 'en')

    def testCreateContributeElement(self):
        """ Test for writing of contribute element """
        cpw = CPWriter()
        doc = minidom.Document()
        LOM_version = 'LOMv1.0'
        lang = 'en'
        cpw._createContributeElement(doc, 'http://enpraxis.net', LOM_version, 'unknown', lang, entities=['test', 'test creator', 'Test creator'], date='2009-05-12 15:07:34', email='user@enpraxis.net')
        con = doc.getElementsByTagNameNS('http://enpraxis.net','contribute')
        rn = doc.getElementsByTagName('role')
        val_node = rn[0].getElementsByTagName('value')
        val = val_node[0].getElementsByTagName('langstring')
        sn_node = rn[0].getElementsByTagName('source')
        sn = sn_node[0].getElementsByTagName('langstring')
        ent = con[0].getElementsByTagName('centity')
        dtn = con[0].getElementsByTagName('date')
        dttn = dtn[0].getElementsByTagName('datetime')        
        valval = val[0].childNodes[0].nodeValue
        snval = sn[0].childNodes[0].nodeValue
        dttnval = dttn[0].childNodes[0].nodeValue
        self.assertEqual(valval, 'unknown')
        self.assertEqual(snval, 'LOMv1.0')
        self.assertEqual(dttnval, '2009-05-12 15:07:34')
        self.assertEqual(len(ent), 3)

    def testCreateVCard(self):
        """ Test creating of VCard element """
        cpw = CPWriter()
        vcard = cpw._createVCard('Test User', 'test-user@enpraxis.net')
        self.assertNotEqual(vcard.find('BEGIN:VCARD\n'), -1)
        self.assertNotEqual(vcard.find('FN:Test User'), -1)
        self.assertNotEqual(vcard.find('EMAIL;INTERNET:test-user@enpraxis.net'), -1)
        self.assertNotEqual(vcard.find('END:VCARD'), -1)

    def testWriteResourceFile(self):
        """ Test writing of resource file """ 
        cpw = CPWriter()
        doc = minidom.Document()
        cpw.writeResourceFile(doc, 'test-module/test-doc.html')
        files = doc.getElementsByTagName('file')
        href = files[0].getAttribute('href')
        self.assertEqual(href, 'test-module/test-doc.html')

    def testGetManifest(self):
        """ Test getting of manifest element """
        cpw = CPWriter()
        doc = cpw.createManifest('008', '2009-06-12 12:00:00')
        man = cpw.getManifest(doc)
        # Check some of the mainfest attributes
        mn = minidom.parseString(man)
        manifest = mn.getElementsByTagName('manifest')
        idval = manifest[0].getAttribute('identifier')
        verval = manifest[0].getAttribute('xmlns:version')
        nsval = manifest[0].getAttribute('xmlns')
        xsival = manifest[0].getAttribute('xsi:schemaLocation')
        self.assertEqual(idval, '008')
        self.assertEqual(verval, '2009-06-12 12:00:00')
        self.assertEqual(nsval, 'http://www.imsglobal.org/xsd/imscp_v1p1')
        self.assertNotEqual(xsival.find('http://www.imsglobal.org/xsd/imscp_v1p1'), -1)

    def testCreateNode(self):
        """ Test creating of individual node """
        cpw = CPWriter()
        doc = minidom.Document()
        tstn = cpw._createNode(doc, 'http://www.enpraxis.net', 'test', '')
        self.assertEqual(tstn.toxml(), '<test xmlns="http://www.enpraxis.net"/>')
        doc = minidom.Document()
        tstn = cpw._createNode(doc, 'http://www.enpraxis.net', 'test', 'test string')
        tstnval = tstn.childNodes[0].nodeValue
        self.assertEqual(tstnval, 'test string')
        self.assertEqual(type(tstnval), type(u''))
        doc = minidom.Document()
        tstn = cpw._createNode(doc, 'http://www.enpraxis.net', 'test', '', attrs=[('testid','009'),('href','test-course/test-doc.html')])
        self.assertEqual(tstn.getAttribute('testid'), '009')
        self.assertEqual(tstn.getAttribute('href'), 'test-course/test-doc.html')

    def testAddNamespaces(self):
        """ Testing of the adding of namespaces """
        cpw = CPWriter()
        doc = minidom.Document()
        tn = doc.createElement('test')
        doc.appendChild(tn)
        namespaces = [('xmlns', 'http://enpraxis.net'),
              ('xmlns:plone','http://plone.org'),]
        cpw.addNamespaces(tn, namespaces)
        self.assertEqual(tn.getAttribute('xmlns'), 'http://enpraxis.net')
        self.assertEqual(tn.getAttribute('xmlns:plone'), 'http://plone.org')
    
    def testGetTextValue(self):
        """ Test getting a text value from a node """
        cpw = CPWriter()
        doc = minidom.Document()
        newnode = doc.createElement('test')
        doc.appendChild(newnode)
        newnode.appendChild(doc.createTextNode(u'Test node text'))
        self.assertEqual(cpw.getTextValue(newnode), 'Test node text')
        # Test without any text node present
        doc = minidom.Document()
        newnode = doc.createElement('test1')
        doc.appendChild(newnode)
        self.assertEqual(cpw.getTextValue(newnode), None)
        # Test with extra space
        doc = minidom.Document()
        newnode = doc.createElement('test1')
        doc.appendChild(newnode)
        newnode.appendChild(doc.createTextNode(u'   Test node text  \n'))
        self.assertEqual(cpw.getTextValue(newnode), 'Test node text')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestCPReader))
    suite.addTest(makeSuite(TestCPWriter))
    return suite
