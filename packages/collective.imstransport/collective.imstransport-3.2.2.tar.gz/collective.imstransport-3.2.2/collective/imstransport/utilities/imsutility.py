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

from zope.interface import implements
from zope.component import getUtility, getUtilitiesFor
from collective.imstransport.utilities.interfaces import IIMSTransportUtility, IIMSManifestWriter, IIMSManifestReader
from OFS.SimpleItem import SimpleItem

class IMSTransportUtility(SimpleItem):

    implements(IIMSTransportUtility)

    def importPackage(self, context, file, packagetype):
        reader = getUtility(IIMSManifestReader, packagetype)
        return reader.readPackage(file, context)
        
    def exportPackage(self, context, file, packagetype):  
        writer = getUtility(IIMSManifestWriter, packagetype)
        return writer.createPackage(file, context)
        
    def getWriters(self):
        writers = getUtilitiesFor(IIMSManifestWriter)
        values = []
        for writer in writers:
            values.append((writer[1].getPackageName(), writer[0]))
        return values

    def getReaders(self):
        utils = getUtilitiesFor(IIMSManifestReader)
        values = []
        for x in utils:
            values.append((x[1].getPackageName(), x[0]))
        return values
