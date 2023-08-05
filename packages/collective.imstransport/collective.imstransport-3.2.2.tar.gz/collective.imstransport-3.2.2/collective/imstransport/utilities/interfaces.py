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

from zope.interface import Interface

class IIMSTransportUtility(Interface):
    """ A utility for the import/export of IMS packages. """

    def importPackage(context, file, packagetype):
        """ Import an IMS Package. """

    def exportPackage(context, file, packagetype):
        """ Export a package. """

    def getReaders():
        """ Get configured reader names. """


class IIMSObjectCreator(Interface):
    """ A utility for creating objects from IMS packages. """
    
    def createObject(data):
        """ Create an object """


class IIMSManifestReader(Interface):
    """ Read manifest data and content from an IMS Package. """

    def getPackageName():
        """ Return the desciptive name of the package type. """

    def readPackage(file, context):
        """ Read IMS CC manifest """


class IIMSManifestWriter(Interface):
    """ Write the IMS Common Cartridge Manifest """
    
    def createPackage(self, file, context):
        """ Writes the IMS CC Manifest """
