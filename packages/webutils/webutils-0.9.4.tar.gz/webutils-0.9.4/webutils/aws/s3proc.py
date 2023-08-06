'''
    Requires Boto AWS library!
    http://code.google.com/p/boto/
'''
import boto
from boto.s3.key import Key


class S3Error(Exception):
    "Misc. S3 Service Error"
    pass


def checkbucket(view_func):
    def _checkbucket(self, *args, **kwargs):
        if self.bucket is None:
            raise S3Error('No assigned bucket. Must run connect()')
        return view_func(self, *args, **kwargs)
    return _checkbucket


class S3Proc(object):
    def __init__(self, aws_key, aws_secret_key, 
                                    bucket, default_perm='private'):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.bucket_name = bucket
        self.conn = None
        self.bucket = None
        self.perm_tuple = (
            'private',
            'public-read',
            'public-read-write',
            'authenticated-read',
        )
        if default_perm not in self.perm_tuple:
            default_perm = 'private'
        self.default_perm = default_perm
    
    def _get_perm(self, perm=None):
        if perm is None or (perm is not None and perm not in self.perm_tuple):
            perm = self.default_perm
        return perm

    def connect(self):
        self.conn = boto.connect_s3(self.aws_key, self.aws_secret_key)
        try:
            self.bucket = self.conn.create_bucket(self.bucket_name)
        except boto.exception.S3ResponseError, err:
            raise S3Error('Error: %i: %s' % (err.status, err.reason))
        except boto.exception.S3CreateError:
            raise S3Error('Unable to create bucket %s' % self.bucket_name)
        return True

    @checkbucket
    def put(self, filename, data, perm=None, fail_silently=True):
        perm = self._get_perm(perm)
        obj = Key(self.bucket)
        obj.key = filename
        obj.set_contents_from_string(data)
        obj.set_acl(perm)
        return True

    @checkbucket
    def put_from_file(self, filename, remote_filename=None, 
                                                perm=None, fail_silently=True):
        ''' Upload file from disk. If you want a different 
            remote filename, specify in remote_filename
        '''
        perm = self._get_perm(perm)
        obj = Key(self.bucket)
        obj.key = remote_filename or filename
        obj.set_contents_from_filename(filename)
        obj.set_acl(perm)
        return True

    @checkbucket
    def get(self, filename):
        ''' Returns file data
        '''
        obj = Key(self.bucket)
        obj.key = filename
        try:
            return obj.get_contents_as_string()
        except boto.exception.S3ResponseError, err:
            raise S3Error('Error: %i: %s' % (err.status, err.reason))

    @checkbucket
    def get_to_file(self, filename, local_filename=None):
        ''' Save file to local filename.
        '''
        obj = Key(self.bucket)
        obj.key = filename
        try:
            obj.get_contents_to_filename(local_filename or filename)
        except boto.exception.S3ResponseError, err:
            raise S3Error('Error: %i: %s' % (err.status, err.reason))
        return True

    @checkbucket
    def delete(self, filename, fail_silently=True):
        ''' Returns true/false on delete 
            Raises S3Error if fail_silently is set to False
        '''
        self.bucket.delete_key(filename)
        return True

    @checkbucket
    def get_perm(self, filename):
        ''' Returns permissions for set file.
        '''
        obj = Key(self.bucket)
        obj.key = filename
        try:
            return obj.get_acl()
        except boto.exception.S3ResponseError, err:
            raise S3Error('Error: %i: %s' % (err.status, err.reason))

    @checkbucket
    def set_perm(self, filename, perm, fail_silently=True):
        ''' Sets permissions on file.
        '''
        perm = self._get_perm(perm)
        obj = Key(self.bucket)
        obj.key = filename
        try:
            obj.set_acl(perm)
        except boto.exception.S3ResponseError, err:
            raise S3Error('Error: %i: %s' % (err.status, err.reason))
        return True

    @checkbucket
    def set_metadata(self, filename, meta_key, meta_value):
        obj = Key(self.bucket)
        obj.key = filename
        try:
            obj.set_metadata(meta_key, meta_value)
        except boto.exception.S3ResponseError, err:
            raise S3Error('Error: %i: %s' % (err.status, err.reason))
        return True

    @checkbucket
    def get_metadata(self, filename, meta_key):
        obj = Key(self.bucket)
        obj.key = filename
        try:
            return obj.get_metadata(meta_key)
        except boto.exception.S3ResponseError, err:
            raise S3Error('Error: %i: %s' % (err.status, err.reason))
