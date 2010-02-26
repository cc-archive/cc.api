
import os

from tests.test_common import *

####################
## Path constants ##
####################
RELAX_ERROR = os.path.join(RELAX_PATH, 'error.relax.xml')
RELAX_ISSUE = os.path.join(RELAX_PATH, 'issue.relax.xml')

##################
## Test classes ##
##################
class TestDetails(TestApi):

    def __init__(self):
        self.uris = ('http://creativecommons.org/licenses/by-nc-nd/2.5/',
                     'http://creativecommons.org/licenses/by-nc-sa/2.5/',
                     'http://creativecommons.org/licenses/by-sa/2.5/',
                     'http://creativecommons.org/licenses/by/2.0/nl/',
                    )

    def test_license_details(self):
        """Test that the license details call responds appropriately."""
        for uri in self.uris:
            res = self.app.get('/details?license-uri=%s' % uri)
            assert relax_validate(RELAX_ISSUE, res.body)

    def test_license_details_post(self):
        """License details accessible through POST also."""
        for uri in self.uris:
            res = self.app.post('/details', params={'license-uri':uri})
            assert relax_validate(RELAX_ISSUE, res.body)

    def test_invalid_params(self):
        """Invalid parameters are ignored."""
        res = self.app.post('/details',
                              params={'license-uri':self.uris[0],
                                      'foo':'bar'
                                     })
        assert relax_validate(RELAX_ISSUE, res.body)
        res = self.app.get('/details?license-uri=%s&foo=bar' % self.uris[0])
        assert relax_validate(RELAX_ISSUE, res.body)


class TestDetailsErrors(TestApi):

    def test_invalid_license(self):
        """Test that an invalid URI raises an error."""
        uri = "http://creativecommons.org/licenses/blarf"
        res = self.app.get('/details?license-uri=%s' % uri)
        assert relax_validate(RELAX_ERROR, res.body)

    def test_no_uri(self):
        """No license-uri causes missingparam error."""
        res = self.app.get('/details')
        assert relax_validate(RELAX_ERROR, res.body)
