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
from Products.CMFPlone.utils import _createObjectByType
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from zipfile import ZipFile
from collective.imstransport.IMS_exceptions import ManifestError

class ObjectCreator(object):
    """ Create objects from IMS manifest. """

    implements(IIMSObjectCreator)

    def createObjects(self, objDict, context, source):
        """ Read the manifest """
        for id in objDict:
            data = objDict[id]
            if data['type'] == 'Large File':
                break
            # Recursively create objects based on metadata dictionary
            if id == 'package':
                if data.has_key('file') and getattr(context, 'setText', None):
                    context.setText(source.readFile(data['file']))
                self.applyMetadata(context, data)
            else:
                parent = self.createFolderPath(context, data['path'])
                exobj = getattr(parent.aq_inner.aq_explicit, data['id'], None)
                if exobj and exobj.portal_type == data['type']:
                    obj = getattr(parent, data['id'])
                else:
                    _createObjectByType(data['type'], parent, data['id'])
                    obj = getattr(parent, data['id'])
                if data['type'] == 'Image' and getattr(obj, 'setImage', None):
                    if data.has_key('file'):
                        filedata = source.readFile(data['file'])
                        obj.setImage(filedata)
                elif data['type'] == 'File' and getattr(obj, 'setFile', None):
                    if data.has_key('file'):
                        filedata = source.readFile(data['file'])
                        obj.setFile(filedata)
                elif data['type'] == 'Document' and getattr(obj, 'setText', None):
                    if data.has_key('file'):
                        filedata = source.readFile(data['file'])
                    elif data.has_key('text') and data['text']:
                        filedata = data['text']
                    else:
                        filedata = ''
                    obj.setText(filedata)
                self.applyMetadata(obj, data)
                obj.reindexObject()
            context.reindexObject()

    def applyMetadata(self, obj, data):
        """ Set the metadata on the object """
        for key in data.keys():
            if key not in  ['file', 'id', 'type']:
                field = obj.getField(key)
                if field:
                    mutator = field.getMutator(obj)
                    if mutator:
                        mutator(data[key])
            

    def createFolderPath(self, context, path):
        """" Create folder path """
        temp = context
        pathsplit = path.split('/')
        for path_elem in pathsplit:
            if not path_elem:
                continue
            if path_elem not in temp.keys():
                temp.invokeFactory('Folder', path_elem)
            temp = getattr(temp, path_elem)
            temp.setTitle(path_elem)
            temp.setExcludeFromNav(True)
            temp.reindexObject()
        return temp
