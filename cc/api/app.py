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
web.config.debug = True

urls = ( # tuple of url to resource method mappings
    
    '/',        'cc.api.resources.base.index',
    '/classes', 'cc.api.resources.base.index',
    '/locales', 'cc.api.resources.locales.index',
    '/details', 'cc.api.resources.details.index',
    
    '/license/([a-z]+)', 'cc.api.resources.license.index',
    '/license/([a-z]+)/(issue|get)', 'cc.api.resources.license.issue',
    
    '/simple/chooser',  'cc.api.resources.simple.chooser',
    '/support/jurisdictions', 'cc.api.resources.support.jurisdictions',

    ) 
    
application = web.application(urls, globals(),)

if __name__ == "__main__":
    application.run()
