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
from collective.imstransport.utilities.imscp.cpwriter import CPWriter
from collective.imstransport.utilities.imscp.cpresourcewriter import CPResourceWriter
from collective.imstransport.utilities.imsinterchange import IMSWriter
from collective.imstransport import IMSTransportMessageFactory as _

class IMSCPWriter(IMSWriter):
    """ Write an IMS content package manifest file. """

    def createPackage(self, filename, context):
        """ Creates an IMS Package """

        destination = ZipfileWriter(context, file)

        cpw = CPWriter()

        # Create the Manifest
        manId = self._createPathId(context.virtual_url_path(), 'MAN')
        manVer = context.ModificationDate()
        doc = cpw.createManifest(manId, manVer)

        # Add top level metadata
        lang = context.Language()
        if not lang:
            lang = context.portal_properties.site_properties.getProperty('default_language')
        cpw.writeTopLevelMetadata(doc,
                                  context.getId(),
                                  context.Title(),
                                  context.portal_url(),
                                  lang,
                                  context.Description(),
                                  context.Subject())

        # Write Organizations and Resources
        orgId = self._createPathId(context.virtual_url_path(), 'ORG')
        orgs = cpw.createOrganizations(doc, orgId)
        res = cpw.createResources(doc)

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
                    cpw.writeItem(orgs, itemId, refid, obj.title)
                rn = cpw.writeResource(res, refid, obj.Type(), path)

                id = obj.getId()
                title = obj.Title()
                urlbase = obj.portal_url.getPortalObject().renderBase()
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
                
                md = cpw.createResourceMetadata(rn)
                cpw.writeGeneralNode(md, id, title, 'en', desc, kw)
                cpw.writeLifeCycleNode(md, creators, contrib, mod, None)
                cpw.writeMetaMetadataNode(md, id, urlbase, email, mod, None, contrib)
                cpw.writeTechnicalNode(md, format, size, location)
                cpw.writeRightsNode(md, value, copyright, None)

                if obj.Type() == 'Link':
                    link = cpw.getLinkXml(title, obj.getRemoteUrl())
                    rpath = '%s' %path
                    self._writeObjectData(link, rpath, destination)
                    cpw.writeResourceFile(rn, rpath)
                else:
                    self._writeObjectData(obj, path, destination)
                    cpw.writeResourceFile(rn, path)

        self._writeObjectData(cpw.getManifest(doc), 'imsmanifest.xml', destination)

        if destination:
            return destination.getOutput()
        else:
            return None, None


