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

IMS_schema = 'IMS Common Cartridge'
IMS_version = '1.0.0'
LOM_version = 'LOMv1.0'
LOM_namespace = 'http://ltsc.ieee.org/xsd/LOM'
LOM_IMSCC_namespace = 'http://ltsc.ieee.org/xsd/imscc/LOM'
LOM_CC_namespace = 'http://ltsc.ieee.org/xsd/LOM'
WL_namespace = 'http://www.imsglobal.org/xsd/imswl_v1p0'
IMS_schemainst = 'http://www.w3.org/2001/XMLSchema-instance'

namespaces = [('xmlns', 'http://www.imsglobal.org/xsd/imscc/imscp_v1p1'),
              ('xmlns:lomimscc', LOM_IMSCC_namespace),
              ('xmlns:lom', LOM_CC_namespace),
              ('xmlns:xsi', IMS_schemainst),]

schema_locations = [
    'http://www.imsglobal.org/xsd/imscc/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p0/derived_schema/imscp_v1p2_localised.xsd',
    '%s http://www.imsglobal.org/profile/cc/ccv1p0/derived_schema/domainProfile_2/lomLoose_localised.xsd' %LOM_CC_namespace,
    '%s http://www.imsglobal.org/profile/cc/ccv1p0/derived_schema/domainProfile_1/lomLoose_localised.xsd' %LOM_IMSCC_namespace,]
