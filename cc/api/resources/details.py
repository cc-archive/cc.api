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

from cc.api import support
from cc.api import api_exceptions 
from cc.api.handlers import render_as

class index:
    
    @render_as('xml')
    def GET(self):
        """ Accepts a license uri as an argument and will return
        the RDF and RDFa of a licnsee """
        locale = web.input().get('locale', 'en')
        license_uri = web.input().get('license-uri')
        
        if not license_uri:
            return api_exceptions.missingparam('license-uri')

        try:
            l = cc.license.by_uri(str(license_uri))
        except cc.license.CCLicenseError:
            return api_exceptions.invaliduri()
        
        return support.build_results_tree(l, locale=locale)

    def POST(self):
        return self.GET()
