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

import web
import lxml.etree as ET
import mimeparse
from decorator import decorator

class HandlerClass(type):
    """ metaclass used in request handlers """
    handlers = {}
    types = {}
    def __new__(meta, classname, bases, classDict):
        # keep track of the available `Handler`s
        new_class = type.__new__(meta, classname, bases, classDict)
        # 'xml' => XMLHandler, 'html' => HTMLHandler, etc.
        meta.handlers[new_class.short_name] = new_class
        # 'application/xml' => XMLHandler, 'text/html' => HTMLHandler
        meta.types.update(dict([(t,new_class)for t in new_class.content_types]))

        return new_class

class Handler(object):
    """ Uses the HandlerClass metaclass for registering which Handler
    handles which content-type and mapping the short type identifiers
    used in the decorator to class capable of handlingt that format.

    To extend the handlers available, simply create a class that inherits
    the `Handler` class and implement a method named `repsonse` that returns
    a string response message.
    
    """
    __metaclass__ = HandlerClass
    # the first content_type will be used in the response headers
    content_types = ('text/plain',)
    # this will be the string used in the @content_types decorator
    short_name = 'text'
    # if a response needs to be encoded otherwise, this can be overloaded
    encoding = 'utf-8'
    def __init__(self, *args, **kwargs):
        # set the HTTP Content-Type response header 
        web.header('Content-Type', '%s; charset=%s' % (self.content_types[0],
                                                       self.encoding))
    def response(self, results):
        # all resources that use @content_types will return an lxml etree object
        if not ET.iselement(results):
            return ''.join(
                [ ET.tostring(r, encoding=self.encoding, method='xml')
                  for r in results ] )
        # the xml response had a root element...
        return ET.tostring(results, encoding=self.encoding, method='xml' )

class XMLHandler(Handler):

    content_types = ('application/xml', 'application/x-xml', 'text/xml',)
    short_name = 'xml'

    def response(self, results):
        """ serialize the results ElementTree object """

        sig = '<?xml version="1.0" encoding="%s"?>\n' % self.encoding
        if not ET.iselement(results):
            return sig + ''.join([
                ET.tostring(r,pretty_print=True) for r in results])

        else:
            return ET.tostring(results, encoding=self.encoding,
                               method='xml', xml_declaration=True,
                               pretty_print=True)

class HTMLHandler(Handler):

    content_types = ('text/html',)
    short_name = 'html'
    
    def response(self, results):
        """ format the results as html """
        if not ET.iselement(results):
            return ''.join(
                [ ET.tostring(r, encoding=self.encoding,
                              method='html', pretty_print=True)
                  for r in results])

        return ET.tostring(results, encoding=self.encoding,
                           method='html', pretty_print=True)

def render_as(*types):
    def wrap(fn, *args, **kwargs):

        # this needs some thought...
        http_accept = web.ctx.env.get('HTTP_ACCEPT', None)

        assert types, 'At least one type must be passed to content_types.'
        
        supported_types = []
        for shortname in types:
            try:
                
                h = HandlerClass.handlers[shortname]
                supported_types.extend([ t for t in h.content_types ])
                
            except KeyError, e:
                if web.config.debug: raise e
                return web.internalerror()
                
        # use mimeparse to parse the http Accept header string
        # restrict matches to the content types supported
        if http_accept:
            mime_type = mimeparse.best_match(supported_types, http_accept)

            if mime_type == '':
                handler = HandlerClass.handlers[types[0]]
            else:
                handler = HandlerClass.types[mime_type]
        else:
            handler = HandlerClass.handlers[types[0]]
            
        try:
            # if results is not an lxml Element, then the handler will
            # throw an exception. if the resource resulted in anything
            # other than an xml tree then this decorator should not be
            # used for that resource's method.
            try:
                result = fn(*args, **kwargs)
            except Exception, e:
                if web.config.debug: raise e
                return web.internalerror()
            
            return handler().response(result)
            
        except TypeError, e:
            # this decorator is only good for results that are serializable
            if web.config.debug: raise e
            return web.internalerror()
                        
    return decorator(wrap)

def content_type(content_type, encoding='utf-8'):
    def wrap(fn, *args, **kwargs):
        web.header('Content-Type', '%s; charset=%s' % (content_type, encoding))
        return fn(*args, **kwargs)
    return decorator(wrap)
