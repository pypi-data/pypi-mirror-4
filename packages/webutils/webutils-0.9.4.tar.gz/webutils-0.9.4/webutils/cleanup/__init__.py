''' Class to handle the cleanup of files older than X days.
    Useful for deleting old backups, etc.
'''
import os
import datetime
from webutils.cleanup.callback import CleanupCallback


class CleanupError(Exception):
    pass


class Cleanup(object):
    ''' Cleanup Class
    '''
    def __init__(self, path, days=30, delete=False, 
                                    callback=None, callback_data=None):
        if not os.path.exists(path):
            raise CleanupError('Invalid path given: %s' % path)
        
        if not os.path.isdir(path):
            raise CleanupError('Given path (%s) is not a directory' % path)
        
        self.path = path
        self.days = days
        self.delete = delete
        
        if callback is not None:
            callback_data = callback_data or {}
            callback_data.update({
                'path': self.path,
                'days': self.days,
                'delete': self.delete,
            })
            self.callback = callback(**callback_data)
        else:
            self.callback = None
    
    def run_cleanup(self):
        local_time = datetime.datetime.now()
        for fname in os.listdir(self.path):
            full_fname = os.path.join(self.path, fname)
            if os.path.isdir(full_fname):
                # Ignore directories... for now...
                continue

            s = os.stat(full_fname)
            f_time = datetime.datetime.fromtimestamp(s.st_ctime)
            if (local_time - f_time).days > self.days:
                # File is older than self.days allows. Call callback first.
                if self.callback is not None:
                    self.callback.handle_file(self.path, fname)
                    
                if self.delete:
                    # XXX Add try/except here to continue even if errors?
                    os.unlink(full_fname)
                else:
                    print 'File %s older than %i days' % \
                                                (full_fname, self.days)