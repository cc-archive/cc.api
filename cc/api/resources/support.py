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

import cc.license
import web
import lxml.etree as ET

from cc.api.handlers import render_as, content_type

def jurisdictions_dropdown(locale, select=None):
    """ Returns a list of html option element as lxml Element objects.
    If a select tag is specified, an lxml ElementTree is returned where the
    root is an html select tag with options elements as its children. """

    options = []
    juri_selector = 'http://creativecommons.org/international/%s/'
    for juri in cc.license.jurisdictions.list():
        # only include launched juris and ignore 'Unported' because its not
        # really a jurisdiction per se
        if juri.launched and juri.code is not '': 
            option = ET.Element('option', dict(value=juri_selector % juri.code))
            option.text = juri.title(locale)
            options.append(option)

    if select:
        select_tag = ET.Element('select', dict(name=select))
        select_tag.extend(options)
        return select_tag

    return options

class jurisdictions:
    
    @render_as('html')
    def GET(self):
        # collect query string arguments
        locale = web.input().get('locale', 'en')
        select = web.input().get('select', None)

        return jurisdictions_dropdown(locale, select)
        
class jurisdictions_js:

    @content_type('text/plain')
    def GET(self):
        # collect query string arguments
        locale = web.input().get('locale', 'en')
        select = web.input().get('select', None)

        html = jurisdictions_dropdown(locale, select)

        # is there a root <select> tag included
        if ET.iselement(html):
            yield "document.write('<select name=\"%s\">');\n" % \
                  html.attrib['name']
            
        for node in html:
            yield "document.write('%s');\n" % ET.tostring(node)

        if ET.iselement(html):
            yield "document.write('</select>');"

        return
        
            
        
    
