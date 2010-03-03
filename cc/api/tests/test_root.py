
import os

from cc.api.tests.test_common import *

####################
## Path constants ##
####################
RELAX_CLASSES = os.path.join(RELAX_PATH, 'classes.relax.xml')

##################
## Test classes ##
##################
class TestRoot(TestApi):

    def test_synonyms(self):
        """Test that /classes and / are synonyms."""
        root = self.app.get('/').body
        classes = self.app.get('/').body
        assert root == classes

    def test_classes_structure(self):
        """Test the return values of /classes."""
        res = self.app.get('/classes')
        assert relax_validate(RELAX_CLASSES, res.body)

    def test_locales(self):
        """Using locale values returns correct values."""
        for locale in self.data.locales():
            res = self.app.get('/?locale=%s' % locale)
            assert relax_validate(RELAX_CLASSES, res.body)

    def test_default_locale(self):
        """Try default locale."""
        default = self.app.get('/').body
        explicit = self.app.get('/?locale=en').body
        assert default == explicit

    def test_extra_args(self):
        """Extra arguments are ignored."""
        res = self.app.get('/?foo=bar')
        assert relax_validate(RELAX_CLASSES, res.body)
