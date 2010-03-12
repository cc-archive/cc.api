
import os
import lxml.html

from cc.api.tests.test_common import *

####################
## Path constants ##
####################
RELAX_OPTIONS = os.path.join(RELAX_PATH, 'options.relax.xml')
RELAX_SELECT = os.path.join(RELAX_PATH, 'select.relax.xml')

##################
## Test classes ##
##################
class TestSupport(TestApi):

    def test_support_jurisdictions(self):
        """/support/jurisdictions served properly."""
        res = self.app.get('/support/jurisdictions') 
        body = self.makexml(res.body)
        assert relax_validate(RELAX_OPTIONS, body)

    def test_javascript(self):
        """Test javascript wrapper over /support/jurisdictions."""
        res = self.app.get('/support/jurisdictions')
        jsres = self.app.get('/support/jurisdictions.js')

        opts = lxml.html.fromstring(res.body)
        jsopts = jsres.body.strip().split('\n')

        assert len(opts) == len(jsopts)
        
        for i,opt in enumerate(opts):
            assert "document.write('%s');" % lxml.html.tostring(opt) == jsopts[i]

        # attempt with select tag...
        res = self.app.get('/support/jurisdictions?select=testing')
        jsres = self.app.get('/support/jurisdictions.js?select=testing')

        opts = lxml.html.fromstring(res.body)
        jsopts = jsres.body.strip().split('\n')

        #  <select> <options> </select>
        assert (1 + len(opts) + 1) == len(jsopts)

        assert jsopts[0] == "document.write('<select name=\"testing\">');"
        assert opts.attrib['name'] == 'testing'

        jsopts = jsopts[1:-1] # strip off select tags
        for i,opt in enumerate(opts):
            assert "document.write('%s');" % lxml.html.tostring(opt) == jsopts[i]
        

    def test_ignore_extra_args(self):
        """Extra arguments are ignored."""
        res = self.app.get('/support/jurisdictions?foo=bar')
        body = self.makexml(res.body)
        assert relax_validate(RELAX_OPTIONS, body)

    ''' NOTE: locale el causes server error; fix in next implementation
    def test_locale(self):
        """Test locale parameter."""
        for locale in self.data.locales():
            res = self.app.get('/support/jurisdictions?locale=%s' % locale)
            body = self.makexml(res.body)
            assert relax_validate(RELAX_OPTIONS, body)
    '''

    def test_select(self):
        """Test select parameter."""
        res = self.app.get('/support/jurisdictions?select=foo')
        body = res.body.replace('&', '&amp;')
        assert relax_validate(RELAX_SELECT, body)
