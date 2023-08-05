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
from collective.imstransport.utilities.interfaces import IIMSManifestWriter
from collective.imstransport.utilities.packagingio import ZipfileWriter
from collective.imstransport.utilities.moodle.moodlewriter import MoodleWriter
from collective.imstransport.utilities.imsinterchange import IMSWriter
from collective.imstransport import IMSTransportMessageFactory as _

class IMSMoodleWriter(IMSWriter):
    """ Write an IMS content package manifest file. """

    def createPackage(self, filename, context):
        """ Creates an IMS Package """

        destination = ZipfileWriter(context, file)
        mw = MoodleWriter()

        # Create the Manifest
        manId = self._createPathId(context.virtual_url_path(), 'MAN')
        manVer = context.ModificationDate()
        doc = mw.createManifest(manId, manVer)

        # Add top level metadata
        lang = context.Language()
        if not lang:
            lang = context.portal_properties.site_properties.getProperty('default_language')
        mw.writeTopLevelMetadata(doc,
                                  context.getId(),
                                  context.Title(),
                                  context.portal_url(),
                                  lang,
                                  context.Description(),
                                  context.Subject())

        # Write Organizations and Resources
        orgId = self._createPathId(context.virtual_url_path(), 'ORG')
        orgs = mw.createOrganizations(doc, orgId)
        res = mw.createResources(doc)

        if orgs and res:
            objs = self._getAllObjects(context)
            for obj in objs:
                # Need to consider excluding folders
                # Get resource info
                path = self._getObjectPath(obj, context)
                vpath = obj.virtual_url_path()
                refid = self._createPathId(vpath, 'RES')
                # Check if we need to add to the organizations section
                if not obj.getExcludeFromNav():
                    itemId = self._createPathId(vpath, 'ITM')
                    mw.writeItem(orgs, itemId, refid, obj.title)
                rn = mw.writeResource(res, refid, obj.Type(), path)

                id = obj.getId()
                title = obj.Title()
                urlbase = obj.portal_url()
                lang = obj.Language()
                if not lang:
                    lang = obj.portal_properties.site_properties.getProperty('default_language')
                desc = obj.Description()
                kw = obj.Subject()
                creators = obj.Creators() 
                contrib = obj.Contributors()
                mod = obj.ModificationDate()
                email = obj.portal_url.getPortalObject().getProperty('email_from_address')
                format = obj.Format()
                size = self.getObjSize(obj)
                location = obj.renderBase()
                value = 'yes'
                rights_holder = obj.portal_properties.site_properties.getProperty('rights_holder')
                rights_holder_email = obj.portal_properties.site_properties.getProperty('rights_holder_email')
                copyright = self._getCopyrightString(obj.Rights(), rights_holder, rights_holder_email)
                
                md = mw.createResourceMetadata(rn)
                mw.writeGeneralNode(md, id, title, 'en', desc, kw)
                mw.writeLifeCycleNode(md, creators, contrib, mod, None)
                mw.writeMetaMetadataNode(md, id, urlbase, email, mod, None, contrib)
                mw.writeTechnicalNode(md, format, size, location)
                mw.writeRightsNode(md, value, copyright, None)

                if obj.Type() == 'Link':
                    link = mw.getLinkXml(title, obj.getRemoteUrl())
                    rpath = '%s' %path
                    self._writeObjectData(link, rpath, destination)
                    mw.writeResourceFile(rn, rpath)
                else:
                    self._writeObjectData(obj, path, destination)
                    mw.writeResourceFile(rn, path)

        self._writeObjectData(mw.getManifest(doc), 'imsmanifest.xml', destination)

        if destination:
            return destination.getOutput()
        else:
            return None, None


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
            from urlparse import urlparse
            if 'text/html' == obj.Format():
                url = urlparse(path)
                if url[2].split('.')[-1] not in ['htm', 'html']:
                    path += '.html'

        return path 


