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

from lxml import etree as ET
from StringIO import StringIO
import re
import json
import web.webapi
import mimerender
from decorator import decorator

class Emitter(object):
    def format(self, results):
        return results

class JSONEmitter(Emitter):
    def format(self, results):
        return json.dumps(results)

class XMLEmitter(Emitter):
    def format(self, results):
        return ET.tostring(results)
    
class HTMLEmitter(XMLEmitter):
    def format(self, results):
        # use XMLEmitter's format logic, but set Content-Type to text/html
        return super(HTMLEmitter, self).format(results)

formatters = {
    mimerender.XML : XMLEmitter,
    mimerender.JSON: JSONEmitter,
    mimerender.HTML: HTMLEmitter,
}

def content_types(*types):
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
    default = types[0] in formatters.keys() and types[0] or 'xml'
    
    # mimerender will however throw an exception for invalid formats,
    # to catch these exceptions the mimerender's decorator is wrapped
    # TODO this needs better explanation
    def wrapper(f, *args, **kwargs):
        """
        mimerender will handle the content negotation based on the headers
        and the query string parameters. emitters is now a mapping of
        media-type short names to a method that can emit the resources'
        returned dicts as xml, json, etc as HTTP responses.
        """
        try:
            return mimerender.mimerender(default,
                                         override_input_key='format',
                                         **emitters)(f)(*args, **kwargs)
        except (mimerender.MimeRenderException, ValueError), e:
            # log the exception
            web.webapi.badrequest()

    return decorator(wrapper)

