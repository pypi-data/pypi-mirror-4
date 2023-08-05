''' General helper functions that are useful to reuse.
'''


def easy_encode(value, enc_type='utf-8', errors='strict'):
    ''' Try to .encode(enc_type) on value.
    '''
    try:
        return value.encode(enc_type, errors)
    except AttributeError:
        return value


def encode_dict(data, enc_type='utf-8', errors='strict'):
    ''' Take a dictionary and encode appropriate variables 
        to specified encoding.
    '''
    for key, value in data.items():
        data[key] = easy_encode(value, enc_type, errors)
    return data


def grab_from_import(module, as_from=False):
    ''' Used to import a object, class, etc. from a Python module. 
    
        Should be used when you want to do the equivilent of
         
            from mymodule import someclass
        
        So you would pass in as the "module" variable:
        
            grab_from_import('mymodule.someclass', as_from=True)
        
        If you simply wanted to do the following:
        
            import mymodule.someclass
        
        You just pass in:
        
            grab_from_import('mymodule.someclass')
        
        The 'default_module' variable will be returned if the 
    '''
    if not as_from:
        return __import__(module, globals(), locals(), [], -1)
    else:
        _pieces = module.split('.')
        _module = '.'.join(_pieces[:-1])
        _obj = _pieces[-1]

        _temp = __import__(_module, globals(), locals(), [_obj,], -1)
        return getattr(_temp, _obj)


def map_translate(data, source, re_map=r'{([\w-]+)}', 
                                src_map='{%s}', allowed_fields=[]):
    ''' Easily create templatized variables for re-use.
        
        By default it will replace any instance of 
        
            {variable_name}
        
        in 'data' with 'source'.variable_name. If 'source' is 
        a dictionary, it will use variable_name as the dictionary 
        key to access the data. Otherwise we will use getattr to 
        grab the data. Accepts callable methods to return data.
        
        data = Data that has template variables
        source = Dictionary or Class type object that contains data 
                 to replace template variables.
        re_map = regular expression to use when matching template 
                 variables
        src_map = Used for actually doing the string replace in the 
                  data variable.
        allowed_fields = List of allowed fields. If specified, then 
                         only fields listed can be templatized.
    '''
    import re
    import copy
    
    def get_translation(source, field):
        if isinstance(source, dict):
            ret = source.get(field, None)
        else:
            ret = getattr(source, field, None)

        if ret is not None and callable(ret):
            ret = ret()
        return str(ret)
    
    new_data = copy.copy(data)
    for field in re.findall(re_map, new_data):
        if allowed_fields and field not in allowed_fields:
            continue
            
        new_data = new_data.replace(
            src_map % field,
            get_translation(source, field),
        )
    return new_data


def strip_unwanted(data, allowed_chars='0123456789'):
    ''' Take "data" variable and strip out every character
        that isn't in "allowed_chars" variable
    '''
    return ''.join([x for x in data if x in allowed_chars])
