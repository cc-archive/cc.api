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
from StringIO import StringIO

import cc.license

from cc.api import api_exceptions 
from cc.api import support
from cc.api.handlers import render_as

class index:
    @render_as('xml')
    def GET(self, selector):
        
        try:
            lclass = cc.license.selectors.choose(selector)
        except cc.license.CCLicenseError:
            return api_exceptions.invalidclass()

        locale = web.input().get('locale', 'en')
        lang = "{http://www.w3.org/XML/1998/namespace}lang"
        
        root = ET.Element('licenseclass', {'id':selector})
        label = ET.SubElement(root, 'label', {lang:locale})
        label.text = lclass.title(locale)
        
        for question in lclass.questions():

            field = ET.SubElement(root, 'field',  {'id':question.id})

            label = ET.SubElement(field, 'label', {lang:locale})
            label.text = question.label(locale)

            desc = ET.SubElement(field, 'description', {lang:locale})
            desc.text = question.description(locale)
            
            ET.SubElement(field, 'type').text = 'enum'

            for a_label, a_id, a_desc in question.answers():
                
                enum = ET.SubElement(field, 'enum',  {'id':a_id})
                label = ET.SubElement(enum, 'label', {lang:locale})
                label.text = a_label

                if a_desc:
                    ET.SubElement(enum,
                                  'description',
                                  {lang:locale}).text = a_desc
                    

        return root

class issue:
    @render_as('xml')
    def POST(self, selector):

        try:
            lclass = cc.license.selectors.choose(selector)
        except cc.license.CCLicenseError:
            return api_exceptions.invalidclass()

        if not web.input().get('answers'):
            return api_exceptions.missingparam('answers')

        try:
            # parse the answers argument into an xml tree
            answers = ET.parse(StringIO(web.input().get('answers')))
            
        except ET.XMLSyntaxError, e:
            return api_exceptions.invalidanswer()

        # converts the answer tree into a dictionary
        # this will trim off any superfluous args in answers
        # it will also perform validation to ensure that the required
        # questions are answered with acceptable value

        try:
            support.validate_answers(lclass, answers)
        except AssertionError, e:
            return api_exceptions.invalidanswer()
        

        answers_dict = support.build_answers_dict(lclass, answers)

        locale = 'en'
        # check if a locale has been passed in answers
        if answers.xpath('/answers/locale'): 
            locale = answers.xpath('/answers/locale')[0].text
            # verify that this is a valid locale
            if locale not in cc.license.locales():
                locale = 'en' # just fallback, don't throw up

        work_dict = {}
        # check if work information was included in the answers
        if answers.xpath('/answers/work-info'):
            work_info = answers.xpath('/answers/work-info')[0]
            # returns a dictionary usable by cc.license formatters
            work_dict = support.build_work_dict(work_info)
        
        # issue the answers dict to the cc.license selector
        license = lclass.by_answers(answers_dict)

        return support.build_results_tree(license, work_dict, locale)
        
class issue_get:
    @render_as('xml')
    def GET(self, selector):
        
        args = web.input()
        locale = str(args.get('locale'))
        if locale not in cc.license.locales():
            locale = 'en'
        
        try:
            lclass = cc.license.selectors.choose(selector)
        except cc.license.CCLicenseError:
            return api_exceptions.invalidclass()

        answers = support.build_answers_xml(lclass, args)
        
        try:
            support.validate_answers(lclass, answers)
        except AssertionError, e:
            return api_exceptions.invalidanswer()
        
        answers_dict = support.build_answers_dict(lclass, answers)
        work_dict = support.build_work_dict(answers)
        
        issued_license = lclass.by_answers(answers_dict)
        
        return support.build_results_tree(issued_license, work_dict, locale)
