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
import cc.license
import lxml.etree as ET
from StringIO import StringIO
from copy import deepcopy

from cc.license.formatters.classes import HTMLFormatter, CC0HTMLFormatter
from cc.api.api_exceptions import missingparam, invaliduri
from cc.api.handlers import content_types

class index:
    
    @content_types('xml', 'html')
    def GET(self):
        """ Accepts a license uri as an argument and will return
        the RDF and RDFa of a licnsee """

        license_uri = web.input().get('license-uri')
        if not license_uri:
            return missingparam('license-uri')

        try:
            l = cc.license.by_uri(str(license_uri))
        except cc.license.CCLicenseError:
            return invaliduri()

        if l.license_code == 'CC0':
            formatter = CC0HTMLFormatter
        else:
            formatter = HTMLFormatter

        root = ET.Element('result')

        # add the license uri and name
        ET.SubElement(root, 'license-uri').text = str(l.uri)
        ET.SubElement(root, 'license-name').text = str(l.title())

        # parse the RDF and RDFa from cc.license
        license_rdf = ET.parse(StringIO(l.rdf))
        license_rdfa = ET.parse(StringIO("<p>%s</p>" % formatter().format(l)))

        # build an empty Work tree
        rdfns = lambda x: '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}%s'%x
        work = ET.Element('Work', { rdfns('about') : '' })
        ET.SubElement(work, 'License', { rdfns('resource') : l.uri })
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
                
