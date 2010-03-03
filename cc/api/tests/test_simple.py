
import os

from cc.api.tests.test_common import *

####################
## Path constants ##
####################
RELAX_OPTIONS = os.path.join(RELAX_PATH, 'options.relax.xml')
RELAX_SELECT = os.path.join(RELAX_PATH, 'select.relax.xml')

##################
## Test classes ##
##################
class TestChooser(TestApi):

    def test_simple_chooser(self):
        """/simple/chooser served properly."""
        res = self.app.get('/simple/chooser') 
        body = self.makexml(res.body)
        assert relax_validate(RELAX_OPTIONS, body)

    def test_javascript(self):
        """Test javascript wrapper over /simple/chooser."""
        res = self.app.get('/simple/chooser')
        jsres = self.app.get('/simple/chooser.js')
        opts = res.body.strip().split('\n')
        jsopts = jsres.body.strip().split('\n')
        assert len(opts) == len(jsopts)
        for i in range(len(opts)):
            assert "document.write('%s');" % opts[i] == jsopts[i]

    def test_ignore_extra_args(self):
        """Extra arguments are ignored."""
        res = self.app.get('/simple/chooser?foo=bar')
        body = self.makexml(res.body)
        assert relax_validate(RELAX_OPTIONS, body)

    def test_exclude(self):
        """Test exclude parameter."""
        for s in ('nc','by','sa','nd'):
            res = self.app.get('/simple/chooser?exclude=%s' % s)
            body = self.makexml(res.body)
            assert relax_validate(RELAX_OPTIONS, body)

    def test_jurisdiction(self):
        """Test jurisdiction parameter."""
        for j in ('uk','us','de','ca'): # TODO: refactor jurisdictions
            res = self.app.get('/simple/chooser?jurisdiction=%s' % j)
            body = self.makexml(res.body)
            assert relax_validate(RELAX_OPTIONS, body)

    ''' NOTE: locale 'el' causes server error; fix in reimplementation
    def test_locale(self):
        """Test locale parameter."""
        for locale in self.data.locales():
            res = self.app.get('/simple/chooser?locale=%s' % locale)
            body = self.makexml(res.body)
            assert relax_validate(RELAX_OPTIONS, body)
    '''

    def test_select(self):
        """Test select parameter."""
        res = self.app.get('/simple/chooser?select=foo')
        assert relax_validate(RELAX_SELECT, res.body)

    def test_unknown_locale(self):
        """Test unknown locale falls back to default."""
        unknown = self.app.get('/simple/chooser?locale=foo').body
        default = self.app.get('/simple/chooser?locale=en').body
        assert unknown == default
