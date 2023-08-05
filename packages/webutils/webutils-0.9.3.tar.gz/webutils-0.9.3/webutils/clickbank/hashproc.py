import hashlib

def thankyou_check(key, data):
    '''
        Verifies hash passed via clickbank site to 
        thank you page.
        https://www.clickbank.com/publisher_tools.html#Publisher_Tools_7
    '''
    if not isinstance(data, dict):
        return False

    try:
        rcpt = data['cbreceipt']
        time = data['time']
        item = data['item']
        cbpop = data['cbpop']
    except KeyError:
        return False

    hash_str = '%s|%s|%s|%s' % (key, rcpt, time, item)
    ckpop = hashlib.sha1(hash_str).hexdigest()[:8].upper()
    return ckpop == cbpop


def ipncheck(key, data):
    '''
        Verifies hash passed via clickbank IPN notification.
        https://www.clickbank.com/20080219_release_summary.html
    '''
    vars = (
        'ccustname',
        'ccustemail',
        'ccustcc',
        'ccuststate',
        'ctransreceipt',
        'cproditem',
        'ctransaction',
        'ctransaffiliate',
        'ctranspublisher',
        'cprodtype',
        'cprodtitle',
        'ctranspaymentmethod',
        'ctransamount',
        'caffitid',
        'cvendthru',
    )

    if not isinstance(data, dict):
        return False

    hash_str = ''
    for var in vars:
        try:
            hash_str += '%s|' % (data[var])
        except KeyError:
            return False

    hash_str += '%s' % (key)
    cbpop = data['cverify']
    ckpop = hashlib.sha1(hash_str).hexdigest()[:8].upper()
    return ckpop == cbpop
