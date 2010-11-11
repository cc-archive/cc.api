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
            assert selector != 'software'
            if selector == 'publicdomain': selector = 'zero'
            lclass = cc.license.selectors.choose(selector)
        except:
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
            assert selector != 'software'
            if selector == 'publicdomain':
                lclass = cc.license.selectors.choose('zero')
            else:
                lclass = cc.license.selectors.choose(selector)
        except:
            return api_exceptions.invalidclass()

        if not web.input().get('answers'):
            return api_exceptions.missingparam('answers')

        try:
            answers_xml = web.input().get('answers')
            if selector == 'publicdomain':
                answers_xml = answers_xml.replace(
                    '<license-publicdomain>',
                    '<license-zero>').replace(
                    '</license-publicdomain>',
                    '</license-zero>')
            
            # parse the answers argument into an xml tree
            answers = ET.parse(StringIO(answers_xml))
            
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
        # issue the answers dict to the cc.license selector
        license = lclass.by_answers(answers_dict)
        
        locale = 'en'
        # check if a locale has been passed in answers
        if answers.xpath('/answers/locale'): 
            locale = answers.xpath('/answers/locale')[0].text
            # verify that this is a valid locale
            if locale not in cc.license.locales():
                locale = 'en' # just fallback, don't throw up

        work_dict = support.build_work_dict(license, answers)
        work_xml = support.build_work_xml(license, answers)
                
        try:
            return support.build_results_tree(license, work_xml,
                                              work_dict, locale)
        except:
            return api_exceptions.pythonerr()
        
class issue_get:
    @render_as('xml')
    def GET(self, selector):
        
        args = web.input()
        locale = str(args.get('locale'))
        if locale not in cc.license.locales():
            locale = 'en'
        
        try:
            assert selector != 'software'
            if selector == 'publicdomain': selector = 'zero'
            lclass = cc.license.selectors.choose(selector)
        except:
            return api_exceptions.invalidclass()

        answers = support.build_answers_xml(lclass, args)
        
        try:
            support.validate_answers(lclass, answers)
        except AssertionError, e:
            return api_exceptions.invalidanswer()
        
        answers_dict = support.build_answers_dict(lclass, answers)
        
        issued_license = lclass.by_answers(answers_dict)
        
        work_dict = support.build_work_dict(issued_license, answers)
        work_xml = support.build_work_xml(issued_license, answers)
        
        try:
            return support.build_results_tree(issued_license, work_xml,
                                              work_dict, locale)
        except:
            return api_exceptions.pythonerr()

class jurisdiction:

    @render_as('xml')
    def GET(self, jid=''):
        
        locale = web.input().get('locale', 'en')

        # return non-newest versions?
        current_only = web.input().get('current', '1')
        current_only = bool(int(current_only))
        
        try:
            j = cc.license.jurisdictions.by_code(str(jid))
            
            if not j.launched:
                raise cc.license.CCLicenseError
        except cc.license.CCLicenseError:
            return api_exceptions.invalidjurisdiction()

        juri = ET.Element('jurisdiction', dict(name=j.title(str(locale)),
                                               url=j.id,
                                               local_url=(j.local_url or '')))

        licenses = cc.license.jurisdictions.get_licenses_by_code(str(jid))

        if current_only:
            current_version = cc.license._lib.functions.current_version('by',
                                                                        str(jid))
        
        for l in licenses:
            license = cc.license.by_uri(l)
            
            if current_only and license.version != current_version:
                continue

            ET.SubElement(juri, 'license', dict(name=license.title(str(locale)),
                                                    url=l))
        
        return juri
