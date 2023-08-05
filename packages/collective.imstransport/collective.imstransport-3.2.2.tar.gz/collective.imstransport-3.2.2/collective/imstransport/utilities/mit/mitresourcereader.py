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
from collective.imstransport.utilities.imscp.cpresourcereader import CPResourceReader
from collective.imstransport.IMS_exceptions import ManifestError

ADLCP_namespace = "http://www.adlnet.org/xsd/adlcp_rootv1p2"
IMSCP_namespace = "http://www.imsglobal.org/xsd/imscp_v1p1"

class MITResourceReader(CPResourceReader):


    def __init__(self, reader, id, lom_namespace):
        """ Constructor for MITResourceReader """
        self.id = id
        self.reader = reader
        self.document = self.reader.document
        self.resource = None
        self.files = []
        self.resdict = {}
        self.href = ''
        self.datafile = ''

        resources = self.document.getElementsByTagName('resources')
        if resources:
            for res in resources[0].getElementsByTagName('resource'):
                if self.id == res.getAttribute('identifier'):
                    self.resource = res
                    self.href = res.getAttribute('href')
                    break

        metadata_nodes = self.resource.getElementsByTagName('metadata')
        if metadata_nodes:
            data_file_nodes = metadata_nodes[0].getElementsByTagNameNS(ADLCP_namespace, 'location')
            if data_file_nodes:
                self.datafile = self.reader.getTextValue(data_file_nodes[0])

        
    def getDataFile(self):
        """ Return the data file """
        return self.datafile




