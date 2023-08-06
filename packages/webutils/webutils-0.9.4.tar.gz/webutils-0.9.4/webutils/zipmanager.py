''' Module to easily create zip files on the fly
'''

import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class ZipError(Exception):
    ''' General zip error calss'''
    pass


class ZipCreate(object):
    ''' Class to manage the creation of zip files
    '''
    def __init__(self):
        self.is_closed = False
        self.zipdata = StringIO()
        self.zfile = zipfile.ZipFile(self.zipdata, 'w')
    
    def add_from_string(self, filename, data):
        assert self.is_closed is False
        try:
            data = data.encode('utf-8')
        except AttributeError:
            pass
        self.zfile.writestr(filename, data)
    
    def mass_import(self, import_list, is_string=True):
        ''' Takes a list or tuple of 2 list/tuples containing 
            the filename and filedata. IE:
            
            (('file1.txt', 'Data for file'), ('file2.txt', 'More data'))
        '''
        if not isinstance(import_list, (list, tuple)):
            raise ZipError('Data passed was not a list or tuple.')
        
        for item in import_list:
            if is_string:
                self.add_from_string(item[0], item[1])
    
    def close(self):
        self.zfile.close()
        self.is_closed = True
    
    def get_zip_data(self):
        if not self.is_closed:
            self.close()
        return self.zipdata.getvalue()
