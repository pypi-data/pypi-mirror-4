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

from Products.CMFCore.interfaces import ISiteRoot
from collective.imstransport import IMSTransportMessageFactory as _
from zope.interface import implements
from collective.imstransport.utilities.interfaces import IIMSManifestReader, IIMSManifestWriter
import md5
from zope.component import getUtility
import re

class IMSReader(object):
    """ Base class for IMS reader objects. """

    implements(IIMSManifestReader)

    def readPackage(self, file, context):
        """ Read IMS manifest. Override this to read specific package info. """

    # Helper functions for readPackage
    def createIdFromFile(self, file):
        """ Get Id from file path """
        return file.split('/')[-1]

    def createPathFromFile(self, file):
        """ Get folder path from file path """
        return '/'.join(file.split('/')[:-1])

    def determineType(self, item, fn):
        """ Determine the type of the item """
        result = 'File'
        docmimetypes = ['text/html', 'text/htm', 'text/plain', 'text/x-rst', 'text/structured']

        if item.has_key('type') and item['type']:
            result = item['type']
        elif item.has_key('Format') and item['Format'] in docmimetypes:
            result = 'Document'
        elif item.has_key('Format') and 'image' in item['Format']:
            result = 'Image'
        else:
            site = getUtility(ISiteRoot)
            mtr = site.mimetypes_registry
            mimetype = mtr.lookupExtension(fn)
            
            if mimetype in docmimetypes:
                result = 'Document'
            elif mimetype and 'image' in str(mimetype):
                result = 'Image'
        return result                    


class IMSWriter(object):
    """ Base class for IMS writer objects. """

    implements(IIMSManifestWriter)

    def _writeObjectData(self, obj, path, destination):
        """ Write file data to the destination object. """
        if type(obj) == type('') or type(obj) == type(u''):
            data = obj        
        else:
            format = ''
            if hasattr(obj.aq_explicit, 'Format'):
                format = obj.Format()
            if obj.Type() in ['File', 'Image'] and hasattr(obj.aq_explicit, 'data'):
                    data = obj.data
            elif 'text/html' == format and hasattr(obj.aq_explicit, 'getText'):
                    data = obj.getText()
            elif format in ['text/plain', 'text/x-rst', 'text/structured'] and hasattr(obj.aq_explicit, 'getRawText'):
                    data = obj.getRawText()
            else:
                data = ''

        if destination:
            destination.writeFile(path, data)

    def _getAllObjects(self, context):
        """ Get all sub objects. """
        objects = [obj.getObject() for obj in context.portal_catalog.searchResults(path={'query':('/'.join(context.getPhysicalPath())+'/'),'depth':-1})]
        return [object for object in objects if not object.isPrincipiaFolderish or getattr(object.aq_explicit, 'getText', None)]

    def _getChildrenObjects(self, parent, objects):
        """ Get objects in current folder """
        parentpath = '/'.join(parent.getPhysicalPath())
        children = []
        for object in objects:
            rpath = '/'.join(object.getPhysicalPath()).replace(parentpath, '')

            if len(rpath.split('/')) == 1:
                children.append(object)
                       
        return children

    def _getObjectPath(self, obj, context):
        """ Get the path of an object. """

        root_path = context.aq_explicit.virtual_url_path()
        obj_path = obj.aq_explicit.virtual_url_path()

        if obj_path.find(root_path) != 0:
            return ''

        # Remove the path of the folder object
        path = obj_path.replace(root_path, '')
        if path and path[0] == '/':
            path = path[1:]

        if not path:
            return ''

        if hasattr(obj.aq_explicit, 'Format'):
            if 'text/html' == obj.Format() and obj.isPrincipiaFolderish:
                path += '.html'

        return path

    def _createPathId(self, path, pre='RES'):
        """ Create a unique id given a path """
        return pre + str(md5.md5(path).hexdigest())

    def _getCopyrightString(self, copyright, rights_holder, rights_holder_email):
        """ Return a copyright string """
        cp = ''
        if copyright:
            cp += copyright
        if rights_holder:
            if cp:
                cp += ', '
            cp += rights_holder
        if rights_holder_email:
            if cp:
                cp += ', '
            cp += rights_holder_email
        return cp
 
    def getObjSize(self, object):
        """ Retrieves the correct size of the object"""
        return '%d' %object.get_size()
