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

            # converts the answer tree into a dictionary
            # this will trim off any superfluous args in answers
            # it will also perform validation to ensure that the required
            # questions are answered with acceptable values
            answers_dict = support.build_answers_dict(lclass, answers)
            
        except (ET.XMLSyntaxError, AssertionError), e:
            # either the etree parse failed or support threw back an
            # exception when the answers tree failed to validate
            return api_exceptions.invalidanswer()

        # issue the answers dict to the cc.license selector
        license = lclass.by_answers(answers_dict)

        return support.build_results_tree(license, work_dict, locale)
        
class issue_get:
    @render_as('xml')
    def GET(self, selector):
        
        answers = { 'work-info': {} }

        """ strictly use strings, cc.license doesn't check `if unicode` before
        a variable reaches a librdf query, which will blow shit up """
        
        if selector == 'standard':
            answers['commercial'] = str(web.input().get('commercial', 'y'))
            answers['derivatives'] = str(web.input().get('derivatives', 'y'))
        elif selector == 'recombo':
            answers['sampling'] = str(web.input().get('sampling', 'sampling'))

        answers['jurisdiction'] = str(web.input().get('jurisdiction', ''))
        answers['locale'] = str(web.input().get('locale', 'en'))

        # dump the extra arguments into the work-info dict
        answers['work-info'].update(dict(
            [(str(k),str(v)) for k,v in web.input().items() if k not in answers]
            ))

        try:
            lclass = cc.license.selectors.choose(selector)
        except cc.license.CCLicenseError:
            return api_exceptions.invalidclass()

        license = lclass.by_answers(answers)

        return support.build_results_tree(license,
                                          answers['work-info'],
                                          answers['locale'])
