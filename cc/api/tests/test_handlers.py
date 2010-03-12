import os

from cc.api.tests.test_common import *
from webtest import TestApp

import web
import webtest
import lxml.etree as ET

from cc.api import handlers

# list of registered handlers
handler_classes = handlers.HandlerClass.handlers.values()

# TODO produce the following classes in a generator

class html:
    @handlers.render_as('html')
    def GET(self):
        return ET.Element('result')

class xml:
    @handlers.render_as('xml')
    def GET(self):
        return ET.Element('result')

class text:
    @handlers.render_as('text')
    def GET(self):
        return ET.Element('result')

class xml_or_html:
    @handlers.render_as('xml', 'html')
    def GET(self):
        return ET.Element('result')

class xml_list:
    @handlers.render_as('text')
    def GET(self):
        return [ ET.Element(char) for char in 'awesome' ]

class invalid_type:
    @handlers.render_as('invalid')
    def GET(self):
        return ET.Element('test')

class invalid_result:
    @handlers.render_as('xml')
    def GET(self):
        return 'testing'

class content_type:
    @handlers.content_type('testing/contenttype')
    def GET(self):
        return 'whatever I want'
    
handler_app = webtest.TestApp(
    web.application(
        ('/html', html,
         '/xml', xml,
         '/text', text,
         '/xml_or_html', xml_or_html,
         '/xml_list', xml_list,
         '/invalid_type', invalid_type,
         '/invalid_result', invalid_result,
         '/content_type', content_type), locals()
        ).wsgifunc()
    )

##################
## Test classes ##
##################

class TestHandlersContentTypes(TestApi):

    def test_sets_contenttype(self):
        """ Response returns content-type based on Accept header """

        for handler in handler_classes:
            # responses will return default type always
            return_type = handler.content_types[0] 
            for content_type in handler.content_types:

                r = handler_app.get('/%s' % handler.short_name,
                                    headers={'Accept': content_type})

                assert r.headers['Content-Type'] == '%s; charset=%s' % \
                                                    (return_type,handler.encoding)
                

    def test_contenttype_fallback(self):
        """ If the Accept header is not supported, fallback to default type """

        for handler in handler_classes:
            # responses will return default type always
            return_type = handler.content_types[0] 
            for content_type in handler.content_types:

                r = handler_app.get('/%s' % handler.short_name,
                                    headers={'Accept': 'superawesome/type'})

                assert r.headers['Content-Type'] == '%s; charset=%s' % \
                                                    (return_type,handler.encoding)
        
    def test_contenttype_no_accept(self):
        """ Fallback to default type if there is not an Accept header. """

        for handler in handler_classes:
            # responses will return default type always
            return_type = handler.content_types[0] 
            for content_type in handler.content_types:

                r = handler_app.get('/%s' % handler.short_name,
                                    headers={'Accept': ''})

                assert r.headers['Content-Type'] == '%s; charset=%s' % \
                                                    (return_type,handler.encoding)

    def test_multi_type_renders(self):
        """ Test that methods decorated with multiple types issue format based on
        the Accept header. """

        html = handler_app.get('/xml_or_html', headers={'Accept':'text/html'})
        xml = handler_app.get('/xml_or_html', headers={'Accept':'text/xml'})

        xml_fallback = handler_app.get('/xml_or_html',
                                       headers={'Accept':'text/json'})
        
        assert html.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert xml.headers['Content-Type'] == 'application/xml; charset=utf-8'
        assert xml_fallback.headers['Content-Type'] == \
               'application/xml; charset=utf-8'

    def test_renders_list_results(self):
        """ If a view returns a list of Elements, then the response should include
        a serialization of all of those elements. """

        r  = handler_app.get('/xml_list')

        assert r.headers['Content-Type'] == 'text/plain; charset=utf-8'
        assert r.body == '<a/><w/><e/><s/><o/><m/><e/>'


    def test_fails_on_invalid_type(self):
        """ Using an invalid type with render_as results in an internal error """

        try:
            r = handler_app.get('/invalid_type')
        except webtest.AppError:
            assert True
        else:
            assert False

    def test_fails_on_invalid_results(self):
        """ Returning non-lxml results in an error when using render_as """

        try:
            r = handler_app.get('/invalid_result')
        except webtest.AppError:
            assert True
        else:
            assert False

    def test_content_type(self):
        """ content_type decorator successfully sets the Content-Type header """

        r = handler_app.get('/content_type')
        assert r.headers['Content-Type'] == 'testing/contenttype; charset=utf-8'
