
import os

from tests.test_common import *

####################
## Path constants ##
####################
RELAX_LOCALES = os.path.join(RELAX_PATH, 'locales.relax.xml')

##################
## Test classes ##
##################
class TestLocales(TestApi):
    """Test /locales functionality."""

    def test_locales(self):
        """Test list of supported languages."""
        res = self.app.get('/locales')
        assert relax_validate(RELAX_LOCALES, res.body)

    def test_locales_extra_args(self):
        """Test extra nonsense args are ignored."""
        res = self.app.get('/locales?foo=bar')
        assert relax_validate(RELAX_LOCALES, res.body)
        res = self.app.get('/locales?lang=en_US&blarf=%s' % hash(res))
        assert relax_validate(RELAX_LOCALES, res.body)
