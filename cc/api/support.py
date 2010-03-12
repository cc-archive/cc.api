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
from copy import deepcopy

import cc.license
from cc.license.formatters.classes import HTMLFormatter, CC0HTMLFormatter

def validate_answers(selector, answers):

    assert answers.xpath('/answers/license-%s' % selector.id), \
           'license-class required'
    
    answers = answers.xpath('/answers/license-%s' % selector.id)[0]
    # don't allow answers to irrelevant questions for this class (except juri)
    for answer in answers:
        assert answer.tag in [ q.id for q in selector.questions() ] or \
               answer.tag == 'jurisdiction', '%s question not allowed.' % answer
    
    for question in selector.questions():
        # assert that the question was answered
        assert answers.xpath(question.id), "%s answer not found." % question.id

        answer = answers.xpath(question.id)[0]
        valid_answers = [ v for l,v,d in question.answers() ]
        if question.id == 'jurisdiction' and answer.text not in valid_answers:
            answer.text = '' # silently fall back to Unported
        
        assert answer.text in valid_answers, "%s not in [%s]." % \
               (answer.text, ','.join(valid_answers))
        
    return True

def build_answers_dict(selector, answers):
    # builds answer dict thats usable in cc.license
    
    answers_dict = {}      
    questions = answers.xpath('/answers/license-%s' % selector.id)[0]
    
    for field in selector.questions():
        answers_dict[field.id] = questions.xpath(field.id)[0].text
    
    return answers_dict

def build_answers_xml(selector, args):
    # build an answers xml tree
    answers = ET.Element('answers')
    questions = ET.SubElement(answers, 'license-%s' % selector.id)
    
    # build the required answer elements
    for question in selector.questions():
        default_answer = question.answers()[0][1]
        ET.SubElement(questions, question.id).text = \
                                 str(args.get(question.id, default_answer))

    # shove anything else in the args dict into the work-info
    work_info = ET.SubElement(answers, 'work-info')
    for field in args:
        if questions.xpath('%s' % field) == [] and \
           answers.xpath('%s' % field) == []:
            # append an element for this argument
            ET.SubElement(work_info, field).text = args[field]

    return answers
    
def build_work_dict(answers):

    work_dict = {}

    if not answers.xpath('/answers/work-info'):
        return work_dict
    
    work_info = answers.xpath('/answers/work-info')[0]
    for item in work_info:
        work_dict[item.tag] = item.text

    if 'type' in work_dict:
        work_dict.setdefault('format', work_dict['type'])
    
    if 'title' in work_dict:
        # don't overwrite the other keys if they exist
        work_dict.setdefault('worktitle', work_dict['title'])
        work_dict.setdefault('work_title', work_dict['title'])
        
    return work_dict

def build_results_tree(license, work_dict=None, locale='en'):

    if license.license_code == 'CC0':
        formatter = CC0HTMLFormatter
    else: # more common case
        formatter = HTMLFormatter

    root = ET.Element('result')
    # add the license uri and name
    ET.SubElement(root, 'license-uri').text = license.uri
    ET.SubElement(root, 'license-name').text = license.title(locale)

    # parse the RDF and RDFa from cc.license
    license_rdf = ET.parse( StringIO(license.rdf) )
    
    # prepare the RDFa for xml parsing
    rdfa = formatter().format(license, work_dict, locale)
    license_rdfa = ET.parse(StringIO('<p>%s</p>' % rdfa))

    # build a Work tree
    rdfns = lambda x: '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}%s'%x
    work = ET.Element('Work', { rdfns('about') : '' })
    ET.SubElement(work, 'license', { rdfns('resource') : license.uri })
    license_rdf.getroot().insert(0, work)
    
    # add RDF trees to the results
    ET.SubElement(root, 'rdf').append(license_rdf.getroot())
    license_rdf = deepcopy(license_rdf)
    ET.SubElement(root,'licenserdf').append(license_rdf.getroot())

    # the html tree has a spurious element at its root that was
    # required for the RDFa to parse, so only append the children
    html = ET.SubElement(root, 'html')
    for element in license_rdfa.getroot().getchildren():
        html.append(element)
    
    return root
