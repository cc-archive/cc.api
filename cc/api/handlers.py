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
    short_name = 'default'
    # if a response needs to be encoded otherwise, this can be overloaded
    charset = 'utf-8'
    def __init__(self, *args, **kwargs):
        # set the HTTP Content-Type response header 
        web.header('Content-Type', '%s; charset=%s' % (self.content_types[0],
                                                       self.charset))
    def response(self, results):
        # all resources that use @content_types will return an lxml etree object
        return ET.tostring(results)

class XMLHandler(Handler):
    content_types = ('application/xml', 'application/x-xml', 'text/xml',)
    short_name = 'xml'
    def response(self, results):
        """ serialize the results ElementTree object """
        sig = '<?xml version="1.0" encoding="utf-8"?>\n'
        return sig + ET.tostring(results, pretty_print=True)

class HTMLHandler(Handler):
    content_types = ('text/html',)
    short_name = 'html'
    def response(self, results):
        """ format the results as html """
        return ET.tostring(results, pretty_print=True)

def content_types(*types):
    def wrap(fn, *args, **kwargs):

        # this needs some thought...
        accept = web.ctx.env.get('HTTP_ACCEPT') or 'text/xml'

        # use mimeparse to parse the http Accept header string
        # restrict matches to the content types supported
        try:
            mime_type = mimeparse.best_match(HandlerClass.types.keys(), accept) 
        except Exception, e:
            return e
            
        if mime_type:
            # find the handler for the requested mime-type
            try:
                handler = HandlerClass.types[mime_type]

                # only use handlers passed into the decorator
                if handler.short_name not in types:
                    return web.webapi.badrequest()

            except KeyError:
                # this mimetype is unsupported
                # fallback to a default Handler, which would be the first
                # handler shortname passed to the decorator
                return web.webapi.badrequest()
        else:
            # if no match is found by mimeparse, then an empty string is
            # returned need to fall back to the default handler in this case
            try:
                handler = HandlerClass.handlers['default']
            except KeyError:
                raise Exception("A default handler has not been set.")
        try:
            # if results is not an lxml Element, then the handler will
            # throw an exception. if the resource resulted in anything
            # other than an xml tree then this decorator should not be
            # used for that resource's method.
            
            return handler().response(fn(*args, **kwargs))
            
        except TypeError:

            # this decorator is only good for results that are serializable
            return web.internalerror()
        
    return decorator(wrap)
