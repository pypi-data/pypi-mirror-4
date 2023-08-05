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
from collective.imstransport.utilities.imscc.ccreader import CCReader
from collective.imstransport.utilities.imscc.ccwriter import CCWriter
from unittest import TestSuite, makeSuite
from xml.dom import minidom

toplevel = """
    <general>
      <identifier>
        <catalog>http://somewhere.com</catalog>
        <entry>asdf</entry>
      </identifier>
      <title>
        <string xml:lang="en">test module</string>
      </title>
      <language>en</language>
      <description>
        <string xml:lang="en">This is a test module</string>
      </description>
      <keyword>
        <string xml:lang="en">test</string>
        <string xml:lang="en">module</string>
        <string xml:lang="en">educational</string>
      </keyword>
    </general>
"""

organizations = """<organizations>
  <organization identifier="1000" structure="rooted-hierarchy">
    <item identifier="1001">
      <item identifier="1002" identifierref="2000" />
      <item identifier="1003" identifierref="2001">
        <title>Test Title</title>
      </item>
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
    <catalog>http://somewhere.com</catalog>
    <entry>asdf</entry>
  </identifier>
  <title>
    <string xml:lang="en">asdf</string>
  </title>
  <language>en</language>
  <description>
    <string xml:lang="en">this is a test</string>
  </description>
  <keyword>
    <string xml:lang="en">Hello</string>
    <string xml:lang="en">There</string>
  </keyword>
</general>
"""

lifecycle = """<lifeCycle>
  <contribute>
    <role>
      <source>
        <string xml:lang="en">LOMv1.0</string>        
      </source>
      <value>
        <string xml:lang="en">author</string>
      </value>
    </role>
    <entity>
BEGIN:VCARD
FN: Sandra Suzannah Serendipity
END:VCARD
    </entity>
    <entity>
BEGIN:VCARD
FN:HUGO
END:VCARD
    </entity>
    <entity>
BEGIN:VCARD
FN: Quincy Adams
END:VCARD
    </entity>
    <date>
      <dateTime>
2009-05-09 15:07:16
      </dateTime>
    </date>
  </contribute>
  <contribute>
    <role>
      <source>
        <string xml:lang="en">LOMv1.0</string>        
      </source>
      <value>
        <string xml:lang="en">unknown</string>
      </value>
    </role>
    <entity>
BEGIN:VCARD
FN:Garth
END:VCARD
    </entity>
    <date>
      <dateTime>
2009-05-11 15:07:16
      </dateTime>
    </date>
  </contribute>
</lifeCycle>
"""

technical = """<technical>
  <format>
    image/png
  </format>
</technical>
"""

rights = """<rights>
  <copyrightAndOtherRestrictions>
    <source>
      LOMv1.0
    </source>
      <value>
        yes
      </value>
   </copyrightAndOtherRestrictions>
   <description>
     <string xml:lang="x-none">This material is copyrighted.</string>
   </description>
</rights>
"""

entity="""<entity>
  BEGIN:VCARD
  FN:  Harrison Cheever
  EMAIL;INTERNET: harrc@plone.org
  END:VCARD
</entity>
"""


linkinfo = """<?xml version="1.0" encoding="utf-8"?>
<wl:webLink xmlns:wl="http://www.imsglobal.org/xsd/imswl_v1p0" xmlns:xsi="xsi:http://www.w3.org/2001/XMLSchema-instance">
	<title>Plone Website</title>
	<url href="http://www.plone.org" target="_blank"/>
</wl:webLink>"""

LOM_IMSCC_namespace = 'http://ltsc.ieee.org/xsd/imscc/LOM'
LOM_namespace = 'http://ltsc.ieee.org/xsd/LOM'
metadata = general + lifecycle


class TestCCReader(IMSTransportTestCase):
    """
    """

    def testParseManifest(self):
        """ Test parsing of manifest node """
        ccr = CCReader()
        doc = ccr.parseManifest('<test>Hello</test>')
        assert(doc.getElementsByTagName('test'))

    def testReadPackageMetadata(self):
        """ Test the reading of package level metadata """
        ccr = CCReader()
        manifest = '<metadata><lom xmlns="%s">' %LOM_IMSCC_namespace + toplevel + '</lom></metadata>'
        doc = ccr.parseManifest(manifest)
        pmd = {}
        ccr.readPackageMetadata(doc, pmd)
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
        ccr = CCReader()
        doc = minidom.parseString(organizations)
        orgs = ccr.readOrganizations(doc)
        assert(orgs)
        self.assertEqual(len(orgs), 3)
        self.assertEqual(orgs['2000'], (1, None))
        self.assertEqual(orgs['2001'], (2, 'Test Title'))

    def testReadResources(self):
        """ Test resource node handling """
        ccr = CCReader()
        doc = minidom.parseString(resources)
        res = ccr.readResources(doc)
        assert(res)
        self.assertEqual('2000', res[0].getAttribute('identifier'))
        self.assertEqual('test.html', res[0].getAttribute('href'))
        self.assertEqual('webcontent', res[0].getAttribute('type'))

    def testGetTextValue(self):
        """ Test removal of text from node """
        document = minidom.parseString('<test>Hello</test>')
        textnode = document.getElementsByTagName('test')[0]
        ccr = CCReader()
        self.assertEqual(ccr.getTextValue(textnode), 'Hello')

    def testReadResourceAttributes(self):
        """ Test resource attributes handling """
        ccr = CCReader()
        doc = ccr.parseManifest(resources)
        res = doc.getElementsByTagName('resource')
        results = ccr.readResourceAttributes(res[0])
        self.assertEqual(results[0], '2000')
        self.assertEqual(results[1], 'webcontent')
        self.assertEqual(results[2], 'test.html')

    def testReadMetadata(self):
        pass

    def testReadGeneral(self):
        """ Test general node handling """
        ccr = CCReader()
        manifest = '<lom xmlns="%s">' %LOM_namespace + general + '</lom>'
        doc = ccr.parseManifest(manifest)
        md = {}
        ccr.readGeneral(doc, md)
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
        ccr = CCReader()
        manifest = '<lom xmlns="%s">' %LOM_namespace + lifecycle + '</lom>'
        doc = ccr.parseManifest(manifest)
        md = {}
        ccr.readLifecycle(doc, md)
        assert(md.has_key('creators'))
        self.assertEqual(md['creators'], ['Sandra Suzannah Serendipity','HUGO','Quincy Adams'])
        assert(md.has_key('contributors'))
        self.assertEqual(md['contributors'], ['Garth'])
        assert(md.has_key('creation_date'))
        self.assertEqual(md['creation_date'], '2009-05-09 15:07:16')

    def testTechnical(self):
        """ Test technical node handling """
        ccr = CCReader()
        manifest = '<lom xmlns="%s">' %LOM_namespace + technical + '</lom>'
        doc = ccr.parseManifest(manifest)
        md = {}
        ccr.readTechnical(doc, md)
        assert(md.has_key('Format'))
        self.assertEqual(md['Format'], 'image/png')


    def testReadRights(self):
        """ Test rights node handling """
        ccr = CCReader()
        manifest = '<lom xmlns="%s">' %LOM_namespace + rights + '</lom>'
        doc = ccr.parseManifest(manifest)
        md = {}
        ccr.readRights(doc, md)
        assert(md.has_key('rights'))
        self.assertEqual(md['rights'],'This material is copyrighted.')

    def testReadLinkInfo(self):
        """ Test reading link """
        ccr = CCReader()
        title, link = ccr.getLinkInfo(linkinfo)
        self.assertEqual(title, 'Plone Website')
        self.assertEqual(link, 'http://www.plone.org')

    def testVcardValues(self):
        """ Testing reading VCards Sections """
        ccr = CCReader()
        manifest = '<lom xmlns="%s">' %LOM_namespace + entity + '</lom>'
        doc = ccr.parseManifest(manifest)
        md = {}
        entity_nodes = doc.getElementsByTagName('entity')
        name, email = ccr.getVcardValues(entity_nodes[0])
        self.assertEqual(name, 'Harrison Cheever')
        self.assertEqual(email, 'harrc@plone.org')

    def testVcardValue(self):
        """ Test reading of VCard line """
        ccr = CCReader()
        text = '\n  FN:    Howard Maggleby \n '
        val = ccr.getVcardValue('FN', text.split('\n'))
        self.assertEqual(val, 'Howard Maggleby')

class TestCCWriter(IMSTransportTestCase):
    """
    """
    
    def testWriteManifest(self):
        """ Test for writing of manifest """
        ccw = CCWriter()
        doc = ccw.createManifest('001', '2009-05-12 15:07:34')
        man = doc.getElementsByTagName('manifest')
        id = man[0].getAttribute('identifier')
        ver = man[0].getAttribute('xmlns:version')
        self.assertEqual(id, '001')
        self.assertEqual(ver, '2009-05-12 15:07:34')

    def testTopLevelMeta(self):
        """ Test for writing of top level metadata """
        ccw = CCWriter()
        doc = ccw.createManifest('001', '2009-05-12 15:07:34')
        LOM_IMSCC_namespace = 'http://ltsc.ieee.org/xsd/imscc/LOM'
	ccw.writeTopLevelMetadata(doc, '001', 'Test Module', 'http://plone.org', 'en', 'This is a test module', ['test','module','educational'])
        man = doc.getElementsByTagName('manifest')
        md = man[0].getElementsByTagName('metadata')
        sch = md[0].getElementsByTagName('schema') 
        ver = md[0].getElementsByTagName('schemaversion')
        lom = md[0].getElementsByTagNameNS(LOM_IMSCC_namespace, 'lom')
        gen = lom[0].getElementsByTagName('general')
        ident = gen[0].getElementsByTagName('identifier')
        cat = ident[0].getElementsByTagName('catalog')
        entry = ident[0].getElementsByTagName('entry')
        tn = gen[0].getElementsByTagName('title')
        tnstr = tn[0].getElementsByTagName('string')
        lang = gen[0].getElementsByTagName('language')
        dn = gen[0].getElementsByTagName('description')
        dnstr = dn[0].getElementsByTagName('string')
        kn = gen[0].getElementsByTagName('keyword')
        knstrs = kn[0].getElementsByTagName('string')
        kws = [kw.childNodes[0].nodeValue for kw in knstrs]
        schval = sch[0].childNodes[0].nodeValue
        verval = ver[0].childNodes[0].nodeValue
        catval = cat[0].childNodes[0].nodeValue
        entryval = entry[0].childNodes[0].nodeValue
        tnstrval = tnstr[0].childNodes[0].nodeValue
        langval = lang[0].childNodes[0].nodeValue
        dnstrval = dnstr[0].childNodes[0].nodeValue
        self.assertEqual(schval, 'IMS Common Cartridge')
        self.assertEqual(verval, '1.0.0')
        self.assertEqual(catval, 'http://plone.org')
        self.assertEqual(entryval, '001')
        self.assertEqual(tnstrval, 'Test Module')
        self.assertEqual(langval, 'en')
        self.assertEqual(dnstrval, 'This is a test module')
        self.assertEqual(kws, ['test', 'module', 'educational'])

    def testCreateOrganizations(self):
        """ Test for writing of organizations, organization, and shell item elements """
        ccw = CCWriter()
        doc = ccw.createManifest('001', '2009-05-12 15:07:34')
        man = doc.getElementsByTagName('manifest')
        ccw.createOrganizations(doc, 'org001', 'item001')
        man = doc.getElementsByTagName('manifest')
        orgs = man[0].getElementsByTagName('organizations')
        org = orgs[0].getElementsByTagName('organization')
        item = org[0].getElementsByTagName('item')
        orgid = org[0].getAttribute('identifier')
        struct = org[0].getAttribute('structure')
        itemid = item[0].getAttribute('identifier')
        self.assertEqual(orgid, 'org001')
        self.assertEqual(struct, 'rooted-hierarchy')
        self.assertEqual(itemid, 'item001')

    def testCreateResources(self):
        """ Test for writing of resources element """
        ccw = CCWriter()
    	doc = ccw.createManifest('001', '2009-05-12 15:07:34')
        ccw.createResources(doc)
        man = doc.getElementsByTagName('manifest')
        resources = man[0].getElementsByTagName('resources')
        assert(resources)
        
    def testWriteItem(self):
        """ Test for writing of a single element """
        ccw = CCWriter()
    	doc = ccw.createManifest('001', '2009-05-12 15:07:34')
        ccw.createOrganizations(doc, 'org001', 'item001')
        orgs = doc.getElementsByTagName('organizations')
        title = ccw.writeItem(orgs[0], 'item002', 'res002', 'This is a test item')
        itn = orgs[0].getElementsByTagName('item')
        # Get the last item added and verify attributes
        itemid = itn[-1].getAttribute('identifier')
        refid = itn[-1].getAttribute('identifierref')
        tnstr = title.childNodes[0].nodeValue
        self.assertEqual(itemid, 'item002')
        self.assertEqual(refid, 'res002')
        self.assertEqual(tnstr, 'This is a test item')

    def testWriteResource(self):
        """ Test for single of resource element """
        ccw = CCWriter()
    	doc = ccw.createManifest('001', '2009-05-12 15:07:34')
        res = ccw.createResources(doc)
        rn1 = ccw.writeResource(res, 'res002', 'Link', 'test-module/test.gif')
        rn2 = ccw.writeResource(res, 'res003', 'Document', 'test-module/index.html')
        idval1 = rn1.getAttribute('identifier')
        typeval1 = rn1.getAttribute('type')
        hrefval1 = rn1.getAttribute('href')        
        idval2 = rn2.getAttribute('identifier')
        typeval2 =  rn2.getAttribute('type')
        hrefval2 = rn2.getAttribute('href')
        self.assertEqual(idval1, 'res002')
        self.assertEqual(typeval1, 'imswl_xmlv1p0')
        self.assertEqual(hrefval1, '')
        self.assertEqual(idval2, 'res003')
        self.assertEqual(typeval2, 'webcontent')
        self.assertEqual(hrefval2, 'test-module/index.html')

    def testCreateResourceMetadata(self):
        """ Test for writing of resource metadata """
        ccw = CCWriter()
    	doc = ccw.createManifest('001', '2009-05-12 15:07:34')
        res = ccw.createResources(doc)
        LOM_namespace = 'http://ltsc.ieee.org/xsd/LOM'
        res = ccw.createResources(doc)
        rn = ccw.writeResource(res, 'res001', 'Document', 'test-module/test-doc.html')
        ccw.createResourceMetadata(rn)
        mdn = rn.getElementsByTagName('metadata')
        lom = mdn[0].getElementsByTagNameNS(LOM_namespace, 'lom')
        assert(lom)

    def testWriteGeneralNode(self):
        """ Test for writing of general node """
        ccw = CCWriter()
        lom = minidom.Document()
        ccw.writeGeneralNode(lom, 'res001', 'Resource 001', 'http://www.plone.org', 'en', 'Test item number 001', ['test', 'module', 'educational'])
        gen = lom.getElementsByTagName('general')
        idn = gen[0].getElementsByTagName('identifier')
        cat = idn[0].getElementsByTagName('catalog')
        ent = idn[0].getElementsByTagName('entry')
        tn = gen[0].getElementsByTagName('title')
        tnstr = tn[0].getElementsByTagName('string')
        lang = gen[0].getElementsByTagName('language')
        dn = gen[0].getElementsByTagName('description')
        dnstr = dn[0].getElementsByTagName('string')
        kn = gen[0].getElementsByTagName('keyword')
        knstrs = kn[0].getElementsByTagName('string')
        kws = [kw.childNodes[0].nodeValue for kw in knstrs]
        entval = ent[0].childNodes[0].nodeValue
        tnstrval = tnstr[0].childNodes[0].nodeValue
        catval = cat[0].childNodes[0].nodeValue
        langval = lang[0].childNodes[0].nodeValue
        dnstrval = dnstr[0].childNodes[0].nodeValue
        self.assertEqual(entval,'res001')
        self.assertEqual(tnstrval,'Resource 001')
        self.assertEqual(catval,'http://www.plone.org')
        self.assertEqual(langval,'en')
        self.assertEqual(dnstrval,'Test item number 001')
        self.assertEqual(kws,['test', 'module', 'educational'])


    def testWriteLifeCycleNode(self):
        """ Test for writing life cycle node """
        ccw = CCWriter()
        lom = minidom.Document()
        ccw.writeLifeCycleNode(lom, ['test-creator1', 'Test creator2'], ['test-contributor1', 'Test Contributor2'], '2009-05-12 15:07:34', 'en')
        ln = lom.getElementsByTagName('lifeCycle')
        an = ln[0].getElementsByTagName('contribute')
        assert(ln)
        self.assertEqual(len(an), 2)

    def testWriteMetaMetadataNode(self):
        """ Test for writing metaMetadata node """
        ccw = CCWriter()
        lom = minidom.Document()        
        ccw.writeMetaMetadataNode(lom, 'res001', 'http://www.enpraxis.net', 'user@enpraxis.net', '2009-05-12 15:07:34', 'en', ['test-contributor1', 'Test Contributor2'])
        mmdn = lom.getElementsByTagName('metaMetadata')
        idn = mmdn[0].getElementsByTagName('identifier')
        cat = idn[0].getElementsByTagName('catalog')
        ent = idn[0].getElementsByTagName('entry')
        mdsc = mmdn[0].getElementsByTagName('metadataSchema')       
        lang = mmdn[0].getElementsByTagName('language')
        cont = mmdn[0].getElementsByTagName('contribute')
        catval = cat[0].childNodes[0].nodeValue
        entval = ent[0].childNodes[0].nodeValue
        mdscval = mdsc[0].childNodes[0].nodeValue
        langval = lang[0].childNodes[0].nodeValue
        self.assertEqual(catval, 'http://www.enpraxis.net,user@enpraxis.net')
        self.assertEqual(entval, 'res001')
        self.assertEqual(mdscval, 'LOMv1.0')
        self.assertEqual(langval, 'en')
        self.assertEqual(len(cont), 1)

    def testWriteTechnicalNode(self):
        """ Test for writing of technical node """
        ccw = CCWriter()
        lom = minidom.Document()
        ccw.writeTechnicalNode(lom, 'text/html', '22', 'http://enpraxis.net/course/test-file.html')
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
        ccw = CCWriter()
        lom = minidom.Document()
        ccw.writeRightsNode(lom, 'yes', 'Description of test document 001', 'en')
        rights = lom.getElementsByTagName('rights')
        crn = rights[0].getElementsByTagName('copyrightAndOtherRestrictions')
        sn = crn[0].getElementsByTagName('source')
        val = crn[0].getElementsByTagName('value')
        dn = rights[0].getElementsByTagName('description')
        dnstr = dn[0].getElementsByTagName('string')
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
        ccw = CCWriter()
        doc = minidom.Document()
        LOM_version = 'LOMv1.0'
        ccw._createContributeElement(doc, 'http://enpraxis.net', LOM_version, 'unknown', entities=['test', 'test creator', 'Test creator'], date='2009-05-12 15:07:34', email='user@enpraxis.net')
        con = doc.getElementsByTagNameNS('http://enpraxis.net','contribute')
        rn = doc.getElementsByTagName('role')
        val = rn[0].getElementsByTagName('value')
        sn = rn[0].getElementsByTagName('source')
        ent = con[0].getElementsByTagName('entity')
        dtn = con[0].getElementsByTagName('date')
        dttn = dtn[0].getElementsByTagName('dateTime')        
        valval = val[0].childNodes[0].nodeValue
        snval = sn[0].childNodes[0].nodeValue
        dttnval = dttn[0].childNodes[0].nodeValue
        self.assertEqual(valval, 'unknown')
        self.assertEqual(snval, 'LOMv1.0')
        self.assertEqual(dttnval, '2009-05-12 15:07:34')
        self.assertEqual(len(ent), 3)

    def testCreateVCard(self):
        """ Test creating of VCard element """
        ccw = CCWriter()
        vcard = ccw._createVCard('Test User', 'test-user@enpraxis.net')
        self.assertNotEqual(vcard.find('BEGIN:VCARD\n'), -1)
        self.assertNotEqual(vcard.find('FN:Test User'), -1)
        self.assertNotEqual(vcard.find('EMAIL;INTERNET:test-user@enpraxis.net'), -1)
        self.assertNotEqual(vcard.find('END:VCARD'), -1)

    def testWriteResourceFile(self):
        """ Test writing of resource file """ 
        ccw = CCWriter()
        doc = minidom.Document()
        ccw.writeResourceFile(doc, 'test-module/test-doc.html')
        files = doc.getElementsByTagName('file')
        href = files[0].getAttribute('href')
        self.assertEqual(href, 'test-module/test-doc.html')

    def testGetManifest(self):
        """ Test getting of manifest element """
        ccw = CCWriter()
        doc = ccw.createManifest('008', '2009-06-12 12:00:00')
        man = ccw.getManifest(doc)
        # Check some of the mainfest attributes
        mn = minidom.parseString(man)
        manifest = mn.getElementsByTagName('manifest')
        idval = manifest[0].getAttribute('identifier')
        verval = manifest[0].getAttribute('xmlns:version')
        nsval = manifest[0].getAttribute('xmlns')
        xsival = manifest[0].getAttribute('xsi:schemaLocation')
        self.assertEqual(idval, '008')
        self.assertEqual(verval, '2009-06-12 12:00:00')
        self.assertEqual(nsval, 'http://www.imsglobal.org/xsd/imscc/imscp_v1p1')
        self.assertNotEqual(xsival.find('http://www.imsglobal.org/xsd/imscc/imscp_v1p1'), -1)

    def testCreateNode(self):
        """ Test creating of individual node """
        ccw = CCWriter()
        doc = minidom.Document()
        tstn = ccw._createNode(doc, 'http://www.enpraxis.net', 'test', '')
        self.assertEqual(tstn.toxml(), '<test xmlns="http://www.enpraxis.net"/>')
        doc = minidom.Document()
        tstn = ccw._createNode(doc, 'http://www.enpraxis.net', 'test', 'test string')
        tstnval = tstn.childNodes[0].nodeValue
        self.assertEqual(tstnval, 'test string')
        self.assertEqual(type(tstnval), type(u''))
        doc = minidom.Document()
        tstn = ccw._createNode(doc, 'http://www.enpraxis.net', 'test', '', attrs=[('testid','009'),('href','test-course/test-doc.html')])
        self.assertEqual(tstn.getAttribute('testid'), '009')
        self.assertEqual(tstn.getAttribute('href'), 'test-course/test-doc.html')

    def testAddNamespaces(self):
        """ Testing of the adding of namespaces """
        ccw = CCWriter()
        doc = minidom.Document()
        tn = doc.createElement('test')
        doc.appendChild(tn)
        namespaces = [('xmlns', 'http://enpraxis.net'),
              ('xmlns:plone','http://plone.org'),]
        ccw.addNamespaces(tn, namespaces)
        self.assertEqual(tn.getAttribute('xmlns'), 'http://enpraxis.net')
        self.assertEqual(tn.getAttribute('xmlns:plone'), 'http://plone.org')
    
    def testGetTextValue(self):
        """ Test getting a text value from a node """
        ccw = CCWriter()
        doc = minidom.Document()
        newnode = doc.createElement('test')
        doc.appendChild(newnode)
        newnode.appendChild(doc.createTextNode(u'Test node text'))
        self.assertEqual(ccw.getTextValue(newnode), 'Test node text')
        # Test without any text node present
        doc = minidom.Document()
        newnode = doc.createElement('test1')
        doc.appendChild(newnode)
        self.assertEqual(ccw.getTextValue(newnode), None)
        # Test with extra space
        doc = minidom.Document()
        newnode = doc.createElement('test1')
        doc.appendChild(newnode)
        newnode.appendChild(doc.createTextNode(u'   Test node text  \n'))
        self.assertEqual(ccw.getTextValue(newnode), 'Test node text')

    def testGetLinkXml(self):
        """ Test link xml """
        ccw = CCWriter()
        WL_namespace = 'http://www.imsglobal.org/xsd/imswl_v1p0'
        link = ccw.getLinkXml('Plone', 'http://www.plone.org')
        doc = minidom.parseString(link)
        wls = doc.getElementsByTagNameNS(WL_namespace, 'webLink')
        tn = wls[0].getElementsByTagName('title')
        url = wls[0].getElementsByTagName('url')
        tnval = tn[0].childNodes[0].nodeValue
        urlval = url[0].getAttribute('href')
        self.assertEqual(tnval, 'Plone')
        self.assertEqual(urlval, 'http://www.plone.org')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestCCReader))
    suite.addTest(makeSuite(TestCCWriter))
    return suite
