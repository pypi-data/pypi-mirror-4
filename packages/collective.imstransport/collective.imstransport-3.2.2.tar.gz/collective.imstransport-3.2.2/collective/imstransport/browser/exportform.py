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

from zope.formlib.form import FormFields, action
from zope.interface import Interface
from zope import schema


from zope.interface import Interface, Attribute
from zope.component import getUtility
from collective.imstransport.utilities.interfaces import IIMSTransportUtility
from zope.schema.vocabulary import SimpleVocabulary
from Products.Five.formlib.formbase import EditForm
from zope.schema._bootstrapinterfaces import WrongType
from zope.schema.interfaces import IVocabularyFactory
from zope.schema import TextLine, Choice
from Products.CMFDefault.formlib.widgets import ChoiceRadioWidget
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.app.form.browser.textwidgets import FileWidget
from zipfile import ZipFile, BadZipfile
from StringIO import StringIO
from collective.imstransport.utilities.interfaces import IIMSManifestWriter
from zope.component import getUtility, getUtilitiesFor
from collective.imstransport import IMSTransportMessageFactory as _



def imswritertypevocabulary(self):

    readers = []
    imsreaders = getUtilitiesFor(IIMSManifestWriter)
    for reader in imsreaders:
        readers.append((reader[0], reader[0]))
    return SimpleVocabulary.fromItems(readers)



class IExport(Interface):
    """ Export Form """

    filename = TextLine(title=_(u"IMS File Export"),
                           description=_(u"The name of the zip file where you want to export the ims package."),
                           required=True)


    packagetype = Choice(title=_(u'Package Type'),
                         description=_(u'The type of package being exported'),
                         required=True,
                         vocabulary='imswritertypevocab')


class ExportFormAdapter(object):
    """ Adapter for the export form """

    implements(IExport)

    def __init__(self,context):
        self.context = context

    def get_zipfile_name(self):
        return self.context.id + '.zip'

    def set_zipfile_name(self, title):
        pass

    def get_type(self):
        return _(u'IMS Common Cartridge')

    def set_type(self):
        pass

    filename = property(get_zipfile_name, set_zipfile_name)
    packagetype = property(get_type, set_type)


class ExportForm(EditForm):
    """ Render the export form  """
    form_fields = FormFields(IExport)
    label = _(u'Export Content')
    description = _(u'Export IMS content package')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.ims_util = getUtility(IIMSTransportUtility)

    @action(_(u'Export') )
    def action_export(self, action, data):

        container = self.context
        filename = self.context.REQUEST['form.filename']
        packagetype = self.context.REQUEST['form.packagetype']

        content, fn = self.ims_util.exportPackage(self.context, filename, packagetype)
         
        if content:
            container.REQUEST.RESPONSE.setHeader('content-type', 'application/zip')
            container.REQUEST.RESPONSE.setHeader('content-length', len(content))
            container.REQUEST.RESPONSE.setHeader('Content-Disposition',
                                                 ' attachment; filename=%s' %filename)
            container.REQUEST.RESPONSE.write(str(content))



