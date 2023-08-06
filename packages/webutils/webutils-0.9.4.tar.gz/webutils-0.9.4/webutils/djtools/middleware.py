from django.conf import settings


class AddIPAddress(object):
    def process_request(self, request):
        request.ip_address = self.get_real_ip(request.META)
        return None

    def get_real_ip(self, meta_data):
        checks = ('HTTP_X_REAL_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR',)
        ip = None
        for check in checks:
            if check in meta_data:
                ip = meta_data[check]
                break
        return ip or ''
