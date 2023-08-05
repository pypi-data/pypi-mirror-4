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
from collective.imstransport.utilities.moodle.backupreader import BackupReader
from unittest import TestSuite, makeSuite
from xml.dom import minidom

mods="""
<MODULES>
  <MOD>
    <ID>1000</ID>
    <MODTYPE>quiz</MODTYPE>
  </MOD>
  <MOD>
    <ID>2000</ID>
    <MODTYPE>resource</MODTYPE>
  </MOD>
  <MOD>
    <ID>3000</ID>
    <MODTYPE>resource</MODTYPE>
  </MOD>
</MODULES>
"""

sections="""
<SECTIONS>
  <SECTION>
      <MODS>
          <MOD>
            <ID>1081</ID>
            <TYPE>quiz</TYPE>
            <INSTANCE>1000</INSTANCE>
            <ADDED>1216752020</ADDED>
            <SCORE>0</SCORE>
            <INDENT>0</INDENT>
            <VISIBLE>1</VISIBLE>
            <GROUPMODE>0</GROUPMODE>
            <GROUPINGID>0</GROUPINGID>
            <GROUPMEMBERSONLY>0</GROUPMEMBERSONLY>
            <IDNUMBER>$@NULL@$</IDNUMBER>
            <ROLES_OVERRIDES>
            </ROLES_OVERRIDES>
            <ROLES_ASSIGNMENTS>
            </ROLES_ASSIGNMENTS>
          </MOD>
          <MOD>
            <ID>1082</ID>
            <TYPE>resource</TYPE>
            <INSTANCE>2000</INSTANCE>
            <ADDED>1216748935</ADDED>
            <SCORE>0</SCORE>
            <INDENT>0</INDENT>
            <VISIBLE>1</VISIBLE>
            <GROUPMODE>0</GROUPMODE>
            <GROUPINGID>0</GROUPINGID>
            <GROUPMEMBERSONLY>0</GROUPMEMBERSONLY>
            <IDNUMBER>$@NULL@$</IDNUMBER>
            <ROLES_OVERRIDES>
            </ROLES_OVERRIDES>
            <ROLES_ASSIGNMENTS>
            </ROLES_ASSIGNMENTS>
          </MOD>
          <MOD>
            <ID>1083</ID>
            <TYPE>resource</TYPE>
            <INSTANCE>3000</INSTANCE>
            <ADDED>1229126603</ADDED>
            <SCORE>0</SCORE>
            <INDENT>0</INDENT>
            <VISIBLE>1</VISIBLE>
            <GROUPMODE>0</GROUPMODE>
            <GROUPINGID>0</GROUPINGID>
            <GROUPMEMBERSONLY>0</GROUPMEMBERSONLY>
            <IDNUMBER>$@NULL@$</IDNUMBER>
            <ROLES_OVERRIDES>
            </ROLES_OVERRIDES>
            <ROLES_ASSIGNMENTS>
            </ROLES_ASSIGNMENTS>
          </MOD>
      </MODS>
  </SECTION>
</SECTIONS>
"""

mod1="""
<MOD>
    <ID>10000</ID>
    <MODTYPE>resource</MODTYPE>
    <NAME>Test Link 1</NAME>
    <TYPE>file</TYPE>
    <REFERENCE>http://www.plone.org</REFERENCE>
    <SUMMARY></SUMMARY>
    <ALLTEXT></ALLTEXT>
    <POPUP></POPUP>
    <OPTIONS>frame</OPTIONS>
    <TIMEMODIFIED>1188332168</TIMEMODIFIED>
</MOD>
"""

mod2="""
<MOD>
    <ID>10100</ID>
    <MODTYPE>resource</MODTYPE>
    <NAME>Test Document 1</NAME>
    <TYPE>text</TYPE>
    <REFERENCE>2</REFERENCE>
    <SUMMARY></SUMMARY>
    <ALLTEXT>Test &amp; Introduction
    </ALLTEXT>
    <POPUP></POPUP>
    <OPTIONS></OPTIONS>
    <TIMEMODIFIED>1241622855</TIMEMODIFIED>
</MOD>
"""

mod3="""
<MOD>
    <ID>10200</ID>
    <MODTYPE>resource</MODTYPE>
    <NAME>Test Internal HTML</NAME>
    <TYPE>file</TYPE>
    <REFERENCE>test-file.html</REFERENCE>
    <SUMMARY></SUMMARY>
    <ALLTEXT></ALLTEXT>
    <POPUP></POPUP>
    <OPTIONS>frame</OPTIONS>
    <TIMEMODIFIED>1229108173</TIMEMODIFIED>
</MOD>
"""

mod4="""
<MOD>
    <ID>10300</ID>
    <MODTYPE>resource</MODTYPE>
    <NAME>Test Internal File</NAME>
    <TYPE>file</TYPE>
    <REFERENCE>test-syllabus.pdf</REFERENCE>
    <SUMMARY></SUMMARY>
    <ALLTEXT></ALLTEXT>
    <POPUP></POPUP>
    <OPTIONS>frame</OPTIONS>
    <TIMEMODIFIED>1229108173</TIMEMODIFIED>
</MOD>
"""

moodletext="""<b>Decription of Test Project</b> <i>$@WORKSHOPVIEWBYID*29057@$</i>"""

class TestBackupReader(IMSTransportTestCase):
    """
    """

    def testParseManifest(self):
        """ Test parsing of manifest node """
        br = BackupReader()
        doc = br.parseMoodleXML('<MOODLE_BACKUP>Hello</MOODLE_BACKUP>')
        assert(br)
        self.assertEqual(br.getTextValue(doc), 'Hello')

    def testReadMods(self):
        """ Test the reading of mods """
        br = BackupReader()
        backup = '<MOODLE_BACKUP>' + mods + '</MOODLE_BACKUP>'
        doc = br.parseMoodleXML(backup)
        mde = br.readMods(doc)
        self.assertEqual(len(mde),2)

    def testReadModAttributes(self):
        """ Test the reading of mod attributes """
        br = BackupReader()
        backup = '<MOODLE_BACKUP>' + mods + '</MOODLE_BACKUP>'
        doc = br.parseMoodleXML(backup)
        mde = br.readMods(doc)
        idm = br.readModAttributes(mde[0])
        self.assertEqual(idm,'2000')

    def testReadSections(self):
        """ Test the reading of sections """
        br = BackupReader()
        backup = '<MOODLE_BACKUP>' + sections + '</MOODLE_BACKUP>'
        doc = br.parseMoodleXML(backup)
        ste = br.readSections(doc)
        self.assertEqual(ste, ['2000','3000'])

    def testReadLink(self):
        """ Test the reading of resource metadata """
        br = BackupReader()
        backup = '<MOODLE_BACKUP><MODULES>' + mod1 + '</MODULES></MOODLE_BACKUP>'
        doc = br.parseMoodleXML(backup)
        mde = br.readMods(doc)
        md1 = br.readResourceMetadata(mde[0])
        md1['type'] = 'Link'
        md1['path'] = ''
        md1['file'] = 'http://www.plone.org'
        md1['title'] = u'Test Link 1'

    def testReadDocument(self):
        """ Test the reading of document metadata """
        br = BackupReader()
        backup = '<MOODLE_BACKUP><MODULES>' + mod2 + '</MODULES></MOODLE_BACKUP>'
        doc = br.parseMoodleXML(backup)
        mde = br.readMods(doc)
        md2 = br.readResourceMetadata(mde[0])
        md2['text'] = u'Test & Introduction'
        md2['path'] = ''
        md2['Format'] = 'text/plain'
        md2['title'] = u'Test Document 1'

    def testReadInternalHTML(self):
        """ Test the reading of internal html file metadata """
        br = BackupReader()
        backup = '<MOODLE_BACKUP><MODULES>' + mod3 + '</MODULES></MOODLE_BACKUP>'
        doc = br.parseMoodleXML(backup)
        mde = br.readMods(doc)
        md3 = br.readResourceMetadata(mde[0])
        md3['path'] = ''
        md3['file'] = 'course_files/test-file.html'
        md3['title'] = u'Test Internal HTML'

    def testReadInternalFile(self):
        """ Test the reading of internal file metadata """
        br = BackupReader()
        backup = '<MOODLE_BACKUP><MODULES>' + mod4 + '</MODULES></MOODLE_BACKUP>'
        doc = br.parseMoodleXML(backup)
        mde = br.readMods(doc)
        md4 = br.readResourceMetadata(mde[0])
        md4['path'] = ''
        md4['file'] = 'course_files/test-syllabus.pdf'
        md4['title'] = u'Test Internal File'

    def testRunFilters(self):
        """ Test the running of filters """
        br = BackupReader()
        net = br.runFilters(moodletext,['variables','striphtml'])
        self.assertEqual(net, 'Decription of Test Project ')
        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestBackupReader))
    return suite
