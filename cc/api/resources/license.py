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
from cc.api import api_exceptions
from cc.api.emitters import contenttypes

class index:
    @contenttypes('xml', 'json')
    def GET(self, selector):
        
        try:
            lclass = cc.license.selectors.choose(selector)
        except cc.license.CCLicenseError:
            return api_exceptions.invalidclass()

        locale = web.input().get('locale', 'en')

        questions = []
        for question in lclass.questions():

            enums = []
            for enum in question.answers():
                enum_ele = {
                    '@attributes': {'id': enum[1]},
                    'label': {
                        '@attributes': {'lang': locale},
                        '@text' : enum[0],
                        },
                    }
                if len(enum) > 2 and enum[2] != {}:
                    enum_ele['description'] = {
                        '@attributes': {'lang': locale},
                        '@text': enum[2],
                        }
                    
                enums.append(enum_ele)
                    
            question = {'@attributes':{'id': question.id},
                        'label':{
                            '@attributes':{'lang':locale},
                            '@text': question.label(locale)},
                        'type': {
                            '@text': 'enum'},
                        'enum': enums,
                        'description':{
                            '@attributes':{'lang':locale},
                            '@text': question.description(locale)}}
            questions.append(question)
            
        return {'licenseclass':{'@attributes':{'id':selector},
                                'label':{
                                    '@attributes': {'lang': locale},
                                    '@text': lclass.title(locale)},
                                'field': questions}}

        

        
