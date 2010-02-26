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

def processor(handler):
    results = handler()
    if web.input().get('format', False):
        # determine if there an available emitter for the requested format
        # only concerned with XML for now
        pass
    
    return XMLEmitter().format(results)
    
class XMLEmitter:

    def build_tree(self, parent, children):
        for child in children:
            if type(children[child]) == list:
                for obj in children[child]:
                    if type(obj) == list:
                        ele = ET.Element(child)
                        self.build_tree(ele, obj)
                    elif type(obj == dict):
                        ele = ET.Element(child, obj.get('attributes',None))
                        ele.text = obj.get('text',None)
                    parent.append(ele)
            else:
                ele = ET.Element(child)
                if type(children[child]) == dict:
                    ele.attrib = children[child].get('attributes', None)
                    ele.text = children[child].get('text', None)
                parent.append(child)        
        return parent

    def dict_to_etree(self, d):
        top = list(d)[0]
        root = ET.Element(top, d[top].get('attributes', None))
        root.text = d[top].get('text', None)
        return self.build_tree(root, d[top])
    
    def format(self, results_dict):
        return ET.tostring(self.dict_to_etree(results_dict))
        
