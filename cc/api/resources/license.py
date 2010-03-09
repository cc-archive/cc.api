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

from cc.api import api_exceptions
from cc.api.handlers import render_as

class index:
    @render_as('xml')
    def GET(self, selector):
        
        try:
            lclass = cc.license.selectors.choose(selector)
        except cc.license.CCLicenseError:
            return api_exceptions.invalidclass()

        locale = web.input().get('locale', 'en')

        root = ET.Element('licenseclass', dict(id=selector))
        label = ET.SubElement(root, 'label', dict(lang=locale))
        label.text = lclass.title(locale)
        
        for question in lclass.questions():

            field = ET.SubElement(root, 'field', dict(id=question.id))
            label = ET.SubElement(field, 'label', dict(lang=locale))
            label.text = question.label(locale)

            ET.SubElement(field, 'type').text = 'enum'

            for a_label, a_id, a_desc in question.answers():
                
                enum = ET.SubElement(field, 'enum', dict(id=a_id))
                label = ET.SubElement(enum, 'label', dict(lang=locale))
                label.text = a_label

                if a_desc:
                    ET.SubElement(enum,
                                  'description',
                                  dict(lang=locale)).text = a_desc
                    
            desc = ET.SubElement(field, 'description', dict(lang=locale))
            desc.text = question.description(locale)

        return root


