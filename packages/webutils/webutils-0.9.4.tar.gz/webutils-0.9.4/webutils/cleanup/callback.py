''' Cleanup Callbacks
'''
class CleanupCallback(object):
    ''' Base callback class
        Callback can take any data you send it. 
        It *has* to have a handle_file() method that 
        does the work for each file as it's processed.
    '''
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def handle_file(self, path, fname):
        pass


class AWSCallback(CleanupCallback):
    ''' AWS S3 Callback
    '''
    def __init__(self, *args, **kwargs):
        from webutils.aws.s3proc import S3Proc
        super(AWSCallback, self).__init__(*args, **kwargs)

        self.conn = S3Proc(self.aws_key, self.aws_secret_key, self.bucket)
        self.conn.connect()

    def handle_file(self, path, fname):
        pass