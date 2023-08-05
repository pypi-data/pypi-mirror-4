'''
    Requires Boto AWS library!
    http://code.google.com/p/boto/
'''
import boto

try:
    import cPickle as pickle
except ImportError:
    import pickle
    
from boto.sqs.message import Message


class SQSError(Exception):
    "Misc. S3 Service Error"
    pass


def checkqueue(view_func):
    def _checkqueue(self, *args, **kwargs):
        if self.queue is None:
            raise SQSError('No assigned queue. Must run connect()')
        return view_func(self, *args, **kwargs)
    return _checkqueue


class PickleMessage(Message):
    ''' Simple class to dump/load data into Pythons 
        pickle format upon reading or writing the 
        message body.
        
        Must use set_body and get_body methods to 
        access the data appropriately
        
        XXX: Because Message is not of an object 
        type, the user of super() is not allowed.
        Filed bug report:
        
        http://code.google.com/p/boto/issues/detail?id=311
    '''
    def set_body(self, body):
        new_body = pickle.dumps(body)
        #super(PickleMessage, self).set_body(new_body)
        Message.set_body(self, new_body)
    
    def get_body(self):
        #new_body = super(PickleMessage, self).get_body()
        new_body = Message.get_body(self)
        return pickle.loads(new_body)


class SQSProc(object):
    def __init__(self, aws_key, aws_secret_key, queue):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.queue_name = queue
        self.msg = Message
        self.conn = None
        self.queue = None

    def connect(self):
        self.conn = boto.connect_sqs(self.aws_key, self.aws_secret_key)
        self.queue = self.set_queue(self.queue_name)
        return True
    
    @checkqueue
    def get_all_queues(self):
        return self.conn.get_all_queues()
    
    def set_queue(self, queue_name):
        try:
            queue = self.conn.create_queue(queue_name)
            if self.queue_name != queue_name:
                self.queue_name = queue_name
            return queue
        except boto.exception.SQSError, err:
            raise SQSError('Error: %i: %s' % (err.status, err.reason))
    
    @checkqueue
    def set_message_class(self, new_cls):
        self.msg = new_cls
        self.queue.set_message_class(new_cls)
    
    @checkqueue
    def write(self, data):
        m = self.msg()
        m.set_body(data)
        try:
            return self.queue.write(m)
        except boto.exception.SQSError, err:
            raise SQSError('Error: %i: %s' % (err.status, err.reason))
    
    @checkqueue
    def read(self, timeout=30):
        try:
            return self.queue.read(timeout)
        except boto.exception.SQSError, err:
            raise SQSError('Error: %i: %s' % (err.status, err.reason))
    
    @checkqueue
    def get_messages(self, count=1, timeout=30):
        try:
            return self.queue.get_messages(count, visibility_timeout=timeout)
        except boto.exception.SQSError, err:
            raise SQSError('Error: %i: %s' % (err.status, err.reason))
    
    @checkqueue
    def delete(self, msg):
        try:
            return self.queue.delete_message(msg)
        except boto.exception.SQSError, err:
            raise SQSError('Error: %i: %s' % (err.status, err.reason))
    
    @checkqueue
    def delete_queue(self):
        try:
            self.conn.delete_queue(self.queue)
            self.queue = None
            return True
        except boto.exception.SQSError, err:
            raise SQSError('Error: %i: %s' % (err.status, err.reason))
    
    @checkqueue
    def count(self):
        try:
            return self.queue.count()
        except boto.exception.SQSError, err:
            raise SQSError('Error: %i: %s' % (err.status, err.reason))
