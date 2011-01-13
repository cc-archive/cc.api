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

def chooser_dropdown(jurisdiction, exclude, locale, select=None):
    
    codes = ['by', 'by-sa', 'by-nc', 'by-nd', 'by-nc-nd', 'by-nc-sa', 'mark', 'CC0']

    options = []
    for code in codes:
        l = cc.license.by_code(code, jurisdiction) # fails on CC0 :/
        if filter(lambda e: e in l.uri, exclude):
            continue # license url contains a string found in exclude list
        option = ET.Element('option', dict(value=l.uri))
        option.text = l.title(locale)
        options.append(option)
    
    if select:
        select_tag = ET.Element('select', dict(name=select))
        select_tag.extend(options)
        return select_tag

    return options


class chooser:
    @render_as('html')
    def GET(self):
        """ done this way so that the xml logic isn't serialized """
        # collect query string parameters
        jurisdiction = web.input().get('jurisdiction', None)
        exclude = web.input().get('exclude', [])
        locale = web.input().get('locale', 'en')
        select = web.input().get('select', None)
        # ensure exclude is a list
        if type(exclude) != list: exclude = [exclude]

        return chooser_dropdown(jurisdiction, exclude, locale, select)

class chooser_js:
    @content_type('text/plain')
    def GET(self):
        
        # collect query string parameters
        jurisdiction = web.input().get('jurisdiction', None)
        exclude = web.input().get('exclude', [])
        locale = web.input().get('locale', 'en')
        select = web.input().get('select', None)

        # ensure exclude is a list
        if type(exclude) != list: exclude = [exclude]
        
        html = chooser_dropdown(jurisdiction, exclude, locale, select)
        
        # is there a root <select> tag included
        if ET.iselement(html):
            yield "document.write('<select name=\"%s\">');\n" % \
                  html.attrib['name']
            
        for node in html:
            yield "document.write('%s');\n" % ET.tostring(node)

        if ET.iselement(html):
            yield "document.write('</select>');"

        return 
