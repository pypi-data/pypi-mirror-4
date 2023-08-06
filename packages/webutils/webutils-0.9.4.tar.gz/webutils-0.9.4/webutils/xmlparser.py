''' Copyright 2009 Peter Sanchez <petersanchez@gmail.com>.  
    See BSD-LICENSE for license information.
    
    Parse / Convert XML data.
    
    Example:
    
    {'sales': [
        {'sale': 
            {'id': 1, 'name': 'test1', 'null-field': None}},
        {'sale': 
            {'id': 2, 'name': 'test2'}}
    ]}
    
    Becomes:
    
    <sales type="array">
        <sale>
            <id type="integer">1</id>
            <name>test1</name>
            <null-field nil="true" />
        </sale>
        <sale>
            <id type="integer">2</id>
            <name>test2</name>
        </sale>
    </sales>
    
    And vise versa.
    
    Call Parser().build_request_string() to convert a dictionary to XML.
    
    Call Parser().parse() to convert an XML string to a dictionary.
'''
import xml.etree.cElementTree as ET


class ParserError(Exception):
    pass
    

class Parser(object):
    def get_key(self, element, key, default=None):
        return element.get(key, default)
    
    def is_nil(self, element):
        return (self.get_key(element, 'nil', 'false') == 'true')
    
    def get_type(self, element):
        return self.get_key(element, 'type', 'string')
    
    def get_data(self, element):
        ret = None
        if not self.is_nil(element):
            etype = self.get_type(element)
            if etype == 'integer':
                ret = int(element.text)
            elif etype == 'boolean':
                ret = (element.text == 'true')
            elif etype == 'array':
                ret = [{
                    c.tag: self.parse_children(c),
                } for c in element.getchildren()]
            else:
                if not element.getchildren():
                    ret = element.text
                else:
                    ret = self.parse_children(element)
        return ret
        
    def parse(self, data):
        ret = {}
        try:
            root = ET.XML(data)
        except SyntaxError, err:
            raise ParserError('Invalid XML data given.')
        ret[root.tag] = self.get_data(root)
        return ret

    def parse_children(self, elements):
        ret = {}
        for child in elements:
            ret[child.tag] = self.get_data(child)
        return ret
    
    def parse_errors(self, data):
        try:
            root = ET.XML(data)
        except SyntaxError, err:
            raise ParserError('Invalid XML data given.')
        return [e.text for e in root.findall('error')]
    
    def parse_request(self, zhash, element=None):
        if element is None:
            if len(zhash) > 1:
                raise ParserError('Invalid data dictionary given.')
            key = zhash.keys()[0]
            data = zhash[key]
            element = ET.Element(key)
            self.parse_request(data, element)
            return element

        else:
            etype = None
            if isinstance(zhash, (list, tuple)):
                etype = 'array'
                for item in zhash:
                    self.parse_request(item, element)
            elif isinstance(zhash, dict):
                for key, value in zhash.iteritems():
                    sub = ET.SubElement(element, key)
                    self.parse_request(value, sub)
            elif isinstance(zhash, bool):
                etype = 'boolean'
                element.text = 'true' if zhash else 'false'
            elif isinstance(zhash, int):
                etype = 'integer'
                element.text = str(zhash)
            elif zhash is None:
                element.set('nil', 'true')
            else:
                element.text = str(zhash)
            
            if etype is not None:
                element.set('type', etype)

    def build_request_string(self, zhash):
        return '<?xml version="1.0" encoding="UTF-8"?>%s' % \
                                        ET.tostring(self.parse_request(zhash))
