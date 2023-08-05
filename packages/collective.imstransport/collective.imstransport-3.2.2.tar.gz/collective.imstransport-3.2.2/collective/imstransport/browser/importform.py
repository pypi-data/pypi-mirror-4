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

from zope.interface import Interface, implements
from zope.schema import TextLine, Choice
from zope.schema.vocabulary import SimpleVocabulary
from Products.Five.formlib.formbase import EditForm
from zope.app.form.browser.textwidgets import FileWidget            
from zope.formlib.form import FormFields, action
from zope.component import getUtility, getUtilitiesFor, getMultiAdapter
from collective.imstransport.utilities.imsutility import IIMSTransportUtility
from collective.imstransport.utilities.interfaces import IIMSManifestReader
from collective.imstransport.IMS_exceptions import ManifestError
from collective.imstransport import IMSTransportMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

class ZipFileLine(TextLine):
    
    def validate(self, value):
        pass

def imsreadertypevocabulary(self):
    readers = []
    imsreaders = getUtilitiesFor(IIMSManifestReader)
    for reader in imsreaders:
        readers.append((reader[0], reader[0]))
    return SimpleVocabulary.fromItems(readers)

class IIMSImport(Interface):
    """ IMS Import form """
    
    filename = ZipFileLine(title=_(u'IMS File Import'),
                        description=(_(u'The name of the IMS package on your local machine.')),
                        required=True)

    packagetype = Choice(title=_(u'Package Type'),
                         description=_(u'The type of package being uploaded'),
                         required=True,
                         vocabulary='imsreadertypevocab')

class IMSImportFormAdapter(object):
    """ Adapter for the IMS import form. """
    
    implements(IIMSImport)

    def __init__(self, context):
        self.context = context;

    def get_zipfile_name(self):
        pass

    def set_zipfile_name(self, title):
        pass

    def get_type(self):
        return _(u'IMS Common Cartridge')

    def set_type(self):
        pass
                     
    filename = property(get_zipfile_name, set_zipfile_name)
    packagetype = property(get_type, set_type)


class IMSImportForm(EditForm):
    """ Render the IMS import form. """

    form_fields = FormFields(IIMSImport)
    form_fields['filename'].custom_widget = FileWidget

    description = _(u'Import IMS package')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @action(_(u'Upload'))
    def action_import(self, action, data):
        
        imstrans = getUtility(IIMSTransportUtility)
        filename = self.context.REQUEST['form.filename']
        packagetype = self.context.REQUEST['form.packagetype']
        try:
            imstrans.importPackage(self.context, filename, packagetype)
        except ManifestError, e:
            IStatusMessage(self.request).addStatusMessage(_('Error importing package: %s' % str(e)), type='error')
            url = getMultiAdapter((self.context, self.request), name='absolute_url')()
            return self.request.response.redirect(url + '/@@imsimport_form')
        else:
            IStatusMessage(self.request).addStatusMessage(_('Package imported successfully.'), type='info')
            return self.request.response.redirect('.')




