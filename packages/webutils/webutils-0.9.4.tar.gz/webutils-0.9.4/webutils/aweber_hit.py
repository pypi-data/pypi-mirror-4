import re
import httplib
import urllib


def gen_form_variables(data):
    '''
        data should be the actual form html..
        This function will pull all the hidden variables 
        and assign them to a dictionary. It can be used 
        in the add_aweber_signup method.
    '''
    data_dict = {}
    pat = r'^<input\s+type="hidden"\s+name="(?P<name>[-\w]+)"' + \
          r'\s+value="(?P<value>.*?)".*?>$'
    for x in data.split('\n'):
        x = x.strip()
        m = re.match(pat, x)
        if m is not None:
            data_dict[m.group('name')] = m.group('value')
    return data_dict


def add_aweber_signup(name, email, url_vars, debug=False):
    '''
        Takes 3 variables...
        name = First name (string)
        email = Email address (string)
        url_vars = aweber form variables (dict)
            url_vars = {
                'meta_web_form_id': '111733762',
                'meta_split_id': '',
                'unit': 'xitplan',
                'redirect': 'http://www.xitplan.com/thankyou.html',
                'meta_redirect_onlist': '',
                'meta_adtracking': 'main index',
                'meta_message': '1',
                'meta_required': 'from',
                'meta_forward_vars': '0',
                'name': name,
                'from': email,
            }
    '''
    url_vars.update({'name': name, 'from': email})

    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain',
    }

    params = urllib.urlencode(url_vars)
    conn = httplib.HTTPConnection('www.aweber.com:80')
    conn.request('POST', '/scripts/addlead.pl', params, headers)
    response = conn.getresponse()
    if debug:
        print response.status, response.reason
    conn.close()
