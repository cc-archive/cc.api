## Copyright (c) 2010, John Doig, Creative Commons

## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the "Software"),
## to deal in the Software without restriction, including without limitation
## the rights to use, copy, modify, merge, publish, distribute, sublicense,
## and/or sell copies of the Software, and to permit persons to whom the
## Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
## DEALINGS IN THE SOFTWARE.

import lxml.etree as ET
import web
import re

def processor(handler):
    results = handler()
    if web.input().get('format', False):
        # determine if there an available emitter for the requested format
        # only concerned with XML for now
        pass
    
    return XMLEmitter().format(results)

XML_NS = 'http://www.w3.org/XML/1998/namespace'
class XMLEmitter:

    def build_element(self, node, attrib=None, text=None):
        # need to expand prefixes

        if type(attrib) == dict and attrib.get('lang'):
            attrib['{%s}lang' % XML_NS] = attrib['lang']
            del attrib['lang']
            
        ele = ET.Element(node, attrib)
        ele.text = text
        return ele
    
    def build_tree(self, parent, children, attrib_key, text_key):
        
        for c in filter(lambda e: e not in (attrib_key, text_key), children):
            if type(children[c]) == list:
                for obj in children[c]:
                    if type(obj) == list:
                        ele = self.build_element(c)
                        self.build_tree(ele, obj, attrib_key, text_key)
                    elif type(obj == dict):
                        ele = self.build_element(c,
                                                 obj.get(attrib_key),
                                                 obj.get(text_key))
                        if filter(lambda e: e not in (attrib_key,text_key),obj):
                            self.build_tree(ele, obj, attrib_key, text_key)
                    parent.append(ele)
            else:
                if type(children[c]) == dict:
                    ele = self.build_element(c,
                                             children[c].get(attrib_key),
                                             children[c].get(text_key))
                    if filter(lambda e: e not in (attrib_key, text_key),
                              children[c]):
                        self.build_tree(ele, children[c], attrib_key, text_key)
                else:
                    ele = self.build_element(c)
                parent.append(ele)        
        return parent

    def dict_to_etree(self, d, attrib_key='@attributes', text_key='@text'):
        top = list(d)[0] 
        root = ET.Element(top, d[top].get(attrib_key, None))
        root.text = d[top].get(text_key, None)
        return self.build_tree(root, d[top], attrib_key, text_key)
    
    def format(self, results_dict):
        return ET.tostring(self.dict_to_etree(results_dict))
        
