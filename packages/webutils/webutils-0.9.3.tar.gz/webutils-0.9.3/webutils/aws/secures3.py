import hmac
import time
import base64
import urllib
import hashlib
import urlparse


class SecureS3(object):
    def __init__(self, key, secret_key):
        self.key = key
        self.secret_key = secret_key

    def gen_signature(self, string_to_sign):
        return base64.encodestring(
            hmac.new(
                self.secret_key,
                string_to_sign,
                hashlib.sha1
            ).digest()
        ).strip()

    def get_file_details(self, url):
        ''' Returns bucket name and file from an S3 URL
        '''
        amazon_host = 's3.amazonaws.com'
        s = urlparse.urlparse(url)
        if not s.path or not s.path[1:]:
            raise ValueError('Invalid S3 file passed.')
			
        if s.netloc == amazon_host:
            # s3.amazonaws.com/bucket/file...
            bucket = s.path[1:].split('/')[0]
            filename = '/'.join(s.path[1:].split('/')[1:])
        elif s.netloc.endswith('.%s' % amazon_host):
            # bucket_name.s3.amazonaws.com/file...
            bucket = s.netloc.replace('.%s' % amazon_host, '')
            filename = s.path[1:]
        else:
            # bucket.com/file... (CNAME BUCKET URL)
            bucket = s.netloc
            filename = s.path[1:]

        return (bucket, filename, s.scheme)

    def get_auth_link(self, bucket, filename, 
                      scheme='http', expires=300, timestamp=None):
        ''' Return a secure S3 link with an expiration on the download.

            key: S3 Access Key (login)
            secret_key: S3 Secret Access Key (password)
            bucket: Bucket name
            filename: file path
            expires: Seconds from NOW the link expires
            timestamp: Epoch timestamp. If present, "expires" will not be used.
        '''
        filename = urllib.quote_plus(filename)
        filename = filename.replace('%2F', '/')
        path = '/%s/%s' % (bucket, filename)

        if timestamp is not None:
            expire_time = float(timestamp)
        else:
            expire_time = time.time() + expires

        expire_str = '%.0f' % (expire_time)
        string_to_sign = u'GET\n\n\n%s\n%s' % (expire_str, path)
        params = {
            'AWSAccessKeyId': self.key,
            'Expires': expire_str,
            'Signature': self.gen_signature(string_to_sign.encode('utf-8')),
        }

        return '%s://s3.amazonaws.com/%s/%s?%s' % (
                        scheme, bucket, filename, urllib.urlencode(params))
    
    def get_easy_auth_link(self, url, expires=600):
        ''' url should be the full URL to the secure file hosted on S3.
            examples:
            http://s3.amazonaws.com/your-bucket/yourfile.zip
            http://your-bucket.s3.amazonaws.com/yourfile.zip
            http://media.your-domain.com/yourfile.zip  (CNAME path to S3)
        '''
        try:
            data = self.get_file_details(url)
        except ValueError:
            return None

        return self.get_auth_link(*data[:2], scheme=data[2], expires=expires)