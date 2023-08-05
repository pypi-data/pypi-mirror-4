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

IMS_schema = 'IMS Content Package'
IMS_version = '1.2'
LOM_version = 'LOMv1.0'
LOM_IMSCP_namespace = 'http://www.imsglobal.org/xsd/imsmd_v1p2'

namespaces = [('xmlns', 'http://www.imsglobal.org/xsd/imscp_v1p1'),
              ('xmlns:imscpmd', 'http://www.imsglobal.org/xsd/imsmd_v1p2'),
              ('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance'),]

schema_locations = ['http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p2.xsd',
                    'http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p4.xsd']
