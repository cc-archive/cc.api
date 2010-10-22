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

import lxml.etree as ET
from StringIO import StringIO
from collections import defaultdict
from copy import deepcopy

import cc.license
from cc.license.formatters.classes import *

""" Mapping of arguments names in work-info elements to the
key that cc.license requires.

First order precedence for the keys, i.e keys' order is left intact when
parsing the work-info xml and the value passed to a formatter is based upon
which key is indexed first.

standard keys: attribution_name, attribution_url, work_title,
source_work, more_permissions_url, work_title, format

cc0 keys: work_title, name, actor_href, work_jurisdiction
"""

FORMATTERS = {
    'zero': CC0HTMLFormatter,
    'standard': HTMLFormatter,
    'recombo': HTMLFormatter,
    'publicdomain': PublicDomainHTMLFormatter,
    }

HTML_FORMATTER_KEYS = [
    ('attribution_name', 'attribution_name'),
    ('creator', 'attribution_name'),
    ('holder', 'attribution_name'),

    ('attribution_url', 'attribution_url'),
    ('work-url', 'attribution_url'), 

    ('title', 'work_title'),
    ('source-url', 'source_work'),
    ('type', 'format'),
    ('more_permissions_url', 'more_permissions_url'),

    ]

CC0_FORMATTER_KEYS = [    
    ('title', 'work_title'),

    ('attribution_name', 'name'),
    ('creator', 'name'),
    ('name', 'name'),

    ('attribution_url', 'actor_href'),
    ('actor_href', 'actor_href'),
    
    ('territory', 'work_jurisdiction'),

    ]
    
def validate_answers(selector, answers):
    """ Takes an xml string `answers` and ensures that
    all of the required questions have values for the given
    selector class. Valid answers must be a member of the
    enumeration for that question, if not, then this function
    with throw an exception, signalling to the caller that the
    answers string is not a valid one. """
    
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
    """ cc.license uses a dict form of the answers xml.
    This function converts the xml string `answers` into a python dict. """
    
    answers_dict = {}      
    questions = answers.xpath('/answers/license-%s' % selector.id)[0]
    
    for field in selector.questions():
        answers_dict[field.id] = questions.xpath(field.id)[0].text
    
    return answers_dict

def build_answers_xml(selector, args):
    """ builds an answers xml string for a selector class using
    default answers for the selector's questions. If any other attributes
    were included in the call, they are appended to as part of the
    work-info. """
    
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
    
def build_work_dict(license, answers=None):
    """ Extract work-info elements from the `answers` ElementTree
    and constructs a dict so that it may be passed to a cc.license
    formatter. """
    
    work_dict = {}
    
    if answers is None or \
           not answers.xpath('/answers/work-info') or \
           len(answers.xpath('/answers/work-info')[0]) == 0:
        return work_dict
    
    work_info = answers.xpath('/answers/work-info')[0]

    formatter_keys = (license.license_class == 'zero' and \
                      CC0_FORMATTER_KEYS or HTML_FORMATTER_KEYS)
    
    # iterate through the dict in order of key precedence
    mapping = defaultdict(list)
    for k,v in formatter_keys:
        mapping[v].append(k)

    for formatter_key, work_info_keys in mapping.items():
        for key in work_info_keys: # index work-info in order of key priority
            if work_info.xpath(key): # key is found, assign value and break loop
                work_dict[formatter_key] = work_info.xpath(key)[0].text
                break
    
    return work_dict

def build_work_xml(license, answers=None):
    """ Accept the work-information parameters defined in the api doc's
    and build an RDF-XML tree containing accurate predicates for the
    paremeters contained in the answers xml. """
    
    RDF = lambda p: '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}%s' % p
    DC = lambda p: '{http://purl.org/dc/elements/1.1/}%s' % p
    work_types = ['Text', 'StillImage', 'MovingImage', 'InteractiveResource',
                  'Sound', ]
    
    root = ET.Element('Work', {RDF('about') : ''},
                      {'dc':'http://purl.org/dc/elements/1.1/'})

    if answers is None or \
           not answers.xpath('/answers/work-info') or \
           len(answers.xpath('/answers/work-info')[0]) == 0:
        # add the license element and return
        ET.SubElement(root, 'license', { RDF('resource') : license.uri })
        return root

    work_info = answers.xpath('/answers/work-info')[0]
    
    # <work-url>
    if work_info.xpath('work-url'):
        root.attrib[ RDF('about') ] = work_info.xpath('work-url')[0].text
    # <title>
    if work_info.xpath('title'):
        ET.SubElement(root, DC('title')).text = work_info.xpath('title')[0].text
    # <type>
    if work_info.xpath('type') and \
       work_info.xpath('type')[0].text in work_types:
        ET.SubElement(root, DC('type')).text = \
                            'http://purl.org/dc/dcmitype/' + \
                            work_info.xpath('type')[0].text
    # <year>
    if work_info.xpath('year'):
        ET.SubElement(root, DC('date')).text = work_info.xpath('year')[0].text
    # <description>
    if work_info.xpath('description'):
        ET.SubElement(root, DC('description')).text = \
                            work_info.xpath('description')[0].text
    # <creator>
    if work_info.xpath('creator'):
        ET.SubElement(root, DC('creator')).text = \
                            work_info.xpath('creator')[0].text
    # <holder>
    if work_info.xpath('holder'):
        ET.SubElement(root, DC('rights')).text = \
                            work_info.xpath('holder')[0].text
    # <source-url>
    if work_info.xpath('source-url'):
        ET.SubElement(root, DC('source')).text = \
                            work_info.xpath('source-url')[0].text
        
    ET.SubElement(root, 'license', { RDF('resource') : license.uri })

    return root
                 
def build_results_tree(license, work_xml=None, work_dict=None, locale='en'):
    """ Build an ElementTree to be returned for an issue or details call.
    Properly wraps the formatter markup of a license as a valid xhtml tree.
    """    
    
    root = ET.Element('result')
    # add the license uri and name
    ET.SubElement(root, 'license-uri').text = license.uri
    ET.SubElement(root, 'license-name').text = license.title(locale)
    ET.SubElement(root, 'deprecated').text = \
                        (license.deprecated and u'true' or u'false')
    
    # parse the RDF and RDFa from cc.license
    license_rdf = ET.parse( StringIO(license.rdf) )
    
    # prepare the RDFa for xml parsing
    try:
        formatter = FORMATTERS.get(license.license_class, HTMLFormatter)
        rdfa = formatter().format(license, work_dict, locale)
    except Exception, e:
        # cc.license formatter choked on something
        # such an example would be an invalid work_jurisdiction value passed
        # to the CC0 formatter
        raise e
    
    license_rdfa = ET.parse(StringIO('<p>%s</p>' % rdfa))
    
    # add RDF trees to the results
    ET.SubElement(root, 'rdf').append(license_rdf.getroot())
    copy_of_license_rdf = deepcopy(license_rdf)
    ET.SubElement(root,'licenserdf').append(copy_of_license_rdf.getroot())

    # append the work tree to the rdf result
    if work_xml is None: work_xml = build_work_xml(license)
    license_rdf.getroot().insert(0, work_xml)

    # the html tree has a spurious element at its root that was
    # required for the RDFa to parse, so only append the children
    html = ET.SubElement(root, 'html')
    for element in license_rdfa.getroot().getchildren():
        html.append(element)
    
    return root
