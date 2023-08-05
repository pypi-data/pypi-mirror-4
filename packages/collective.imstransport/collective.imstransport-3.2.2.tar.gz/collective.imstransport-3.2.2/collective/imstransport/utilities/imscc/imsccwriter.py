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

from collective.imstransport.utilities.packagingio import ZipfileWriter
from collective.imstransport.utilities.imscc.ccwriter import CCWriter
from collective.imstransport.utilities.imsinterchange import IMSWriter
from collective.imstransport import IMSTransportMessageFactory as _

class IMSCCWriter(IMSWriter):
    """ Write an IMS content package manifest file. """

    def createPackage(self, file, context):
        """ Creates an IMS Package """

        destination = ZipfileWriter(context, file)

        ccw = CCWriter()

        # Create the Manifest
        manId = self._createPathId(context.virtual_url_path(), 'MAN')
        manVer = context.ModificationDate()
        doc = ccw.createManifest(manId, manVer)

        # Add top level metadata
        lang = context.Language()
        if not lang:
            lang = context.portal_properties.site_properties.getProperty('default_language')
        ccw.writeTopLevelMetadata(doc,
                                  context.getId(),
                                  context.Title(),
                                  context.portal_url(),
                                  lang,
                                  context.Description(),
                                  context.Subject())

        # Write Organizations and Resources
        orgId = self._createPathId(context.virtual_url_path(), 'ORG')
        itemId = self._createPathId(context.virtual_url_path(), 'SHL')
        orgs = ccw.createOrganizations(doc, orgId, itemId)
        res = ccw.createResources(doc)

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
                    ccw.writeItem(orgs, itemId, refid, obj.title)
                rn = ccw.writeResource(res, refid, obj.Type(), path)

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
                mod = obj.ModificationDate().replace(' ','T')
                email = obj.portal_url.getPortalObject().getProperty('email_from_address')
                format = obj.Format()
                size = self.getObjSize(obj)
                location = obj.renderBase()
                value = 'yes'
                rights_holder = obj.portal_properties.site_properties.getProperty('rights_holder')
                rights_holder_email = obj.portal_properties.site_properties.getProperty('rights_holder_email')
                copyright = self._getCopyrightString(obj.Rights(), rights_holder, rights_holder_email)
                
                md = ccw.createResourceMetadata(rn)
                ccw.writeGeneralNode(md, id, title, urlbase, lang, desc, kw)
                ccw.writeLifeCycleNode(md, creators, contrib, mod, lang)
                ccw.writeMetaMetadataNode(md, id, urlbase, email, mod, lang, contrib)
                ccw.writeTechnicalNode(md, format, size, location)
                ccw.writeRightsNode(md, value, copyright, lang)

                if obj.Type() == 'Link':
                    link = ccw.getLinkXml(title, obj.getRemoteUrl())
                    rpath = '%s%s' %(path,'.xml')
                    self._writeObjectData(link, rpath, destination)
                    ccw.writeResourceFile(rn, rpath)
                else:
                    self._writeObjectData(obj, path, destination)
                    ccw.writeResourceFile(rn, path)

        self._writeObjectData(ccw.getManifest(doc), 'imsmanifest.xml', destination)

        if destination:
            return destination.getOutput()
        else:
            return None, None


