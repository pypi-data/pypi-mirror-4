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

from zipfile import ZipFile, ZIP_DEFLATED
from StringIO import StringIO

class FileReader:
    """ Read files from the var directory. """

    def __init__(self, package_path):
        self.fullpath = package_path

    def readManifest(self, manifestfile='imsmanifest.xml'):
        """ Get the manifest file if it exists. """
        manifest_path = os.path.join(self.fullpath, 'imsmanifest.xml')
        file = open(manifest_path, 'rb')
        manifest = file.read()
        file.close()
        return manifest

    def readFile(self, path):
        """ Get file data from the zip file. """
        fullpath = self.fullpath
        for x in path.split('/'):
            fullpath = os.path.join(fullpath, x)
        file = open(fullpath, 'rb')
        data = file.read()
        file.close()
        return data


class ZipfileReader:
    """ Reads files from an imported zip file. """

    def __init__(self, files):
        self.files = ZipFile(files)
        self.fullpath = ''

    def readManifest(self, manifestfile='imsmanifest.xml'):
        """ Get the maifest file if it exists. """
        for x in self.files.namelist():
            index = x.find(manifestfile)
            if index != -1:
                self.fullpath = x[:index]
                return self.files.read(x)
        return None
    
    def readFile(self, path):
        """ Get file data from the zip file. """
        fn = '%s%s' %(self.fullpath, str(path))
        if fn not in self.files.namelist():
            fn = fn.replace('/', '\\')
            if fn not in self.files.namelist():
                return None
        return self.files.read(fn)

    def getFolderFiles(self, path):
        """ Returns the files within a specific folder """
        retfiles = []
        for fn in self.files.namelist():
            if path +'/' in fn:
                retfiles.append(fn)
        return retfiles


class ZipfileWriter:
    """ Write a zip file which contains all the IMS Content packaging stuff. """

    def __init__(self, archive_name, package_name):
        self.fullpath = ''
        self.archive_name = archive_name
        self.package_name = package_name
        self.archive = StringIO()
        self.zipfile = ZipFile(self.archive, 'w', ZIP_DEFLATED)

    def writeFile(self, path, data):
        """ Write a file to the zip archive. """
        fpath = '%s%s' %(self.fullpath, path)
        self.zipfile.writestr(fpath.encode('utf-8'), data)

    def getOutput(self):
        """ Close the zip file and get the binary archive. """
        self.zipfile.close()
        self.archive.seek(0)
        return self.archive.read(), self.archive_name
        


