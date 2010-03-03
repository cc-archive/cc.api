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
import re
import json
import mimerender

class Emitter(object):
    def format(self, **results):
        return results

class JSONEmitter(Emitter):
    def format(self, **results):
        return json.dumps(results)

class XMLEmitter(Emitter):

    XML_NS = 'http://www.w3.org/XML/1998/namespace'
    attrib_key = '@attributes'
    text_key = '@text'

    def child_nodes(self, node):
        return filter(lambda e: e not in (self.attrib_key,self.text_key), node)
    
    def build_element(self, node, attrib=None, text=None):
        # need to expand prefixes

        if type(attrib) == dict and attrib.get('lang'):
            attrib['{%s}lang' % self.XML_NS] = attrib['lang']
            del attrib['lang']
            
        ele = ET.Element(node, attrib)
        ele.text = text
        return ele
    
    def build_tree(self, parent, children):
        
        for c in self.child_nodes(children):
            if type(children[c]) == list:
                for obj in children[c]:
                    if type(obj) == list:
                        ele = self.build_element(c)
                        self.build_tree(ele, obj)
                    elif type(obj == dict):
                        ele = self.build_element(c,
                                                 obj.get(self.attrib_key),
                                                 obj.get(self.text_key))
                        if self.child_nodes(obj):
                            self.build_tree(ele, obj)
                    parent.append(ele)
            else:
                if type(children[c]) == dict:
                    ele = self.build_element(c,
                                             children[c].get(self.attrib_key),
                                             children[c].get(self.text_key))
                    if self.child_nodes(children[c]):
                        self.build_tree(ele, children[c])
                else:
                    ele = self.build_element(c)
                parent.append(ele)        
        return parent

    def dict_to_etree(self, d):
        top = list(d)[0]
        attrib, text = None, None
        if type(d[top]) == dict:
            attrib = d[top].get(self.attrib_key, None)
            text = d[top].get(self.text_key, None)
        root = self.build_element(top, attrib, text)
        return self.build_tree(root, d[top])
    
    def format(self, **results):
        return ET.tostring(self.dict_to_etree(results))

class HTMLEmitter(XMLEmitter):
    def format(self, **results):
        # use XMLEmitter's format logic, but set Content-Type to text/html
        return super(HTMLEmitter, self).format(results)

formatters = {
    mimerender.XML : XMLEmitter,
    mimerender.JSON: JSONEmitter,
    mimerender.HTML: HTMLEmitter,
}

def contenttypes(*types):
    """
    contenttypes is a wrapper to the mimerender decorator.

    When the contenttypes decorator is used, it is to be passed a
    list of string identifying the supported formats for that resource.
    
    The list of available short names to the media-types can be found in
    the keys of the formatters dictionary.
    
    TODO finish documenting here, expecially to explain mimerender
    """
    emitters = {}
    for t in types:
       if t in formatters.keys():
           # all emitter classes must implement format
           emitters[t] = formatters[t]().format 
       # TODO: maybe log/catch if type is unsupported, fallback to text?

    # default to the first type passed to decorator 
    default = types[0] in formatters.keys() and types[0] or 'text'

    # mimerender will handle the content negotation based on the headers and
    # the query string parameters. emitters is now a mapping of media-type
    # short names to a method that can emit the resources' returned dicts
    # as xml, json, etc as HTTP responses.
    return mimerender.mimerender(default,
                                 override_input_key='format',
                                 **emitters)
