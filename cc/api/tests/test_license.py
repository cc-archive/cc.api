
import os

from tests.test_common import *

####################
## Path constants ##
####################
RELAX_ERROR = os.path.join(RELAX_PATH, 'error.relax.xml')
RELAX_LICENSECLASS = os.path.join(RELAX_PATH, 'licenseclass.relax.xml')
RELAX_ISSUE = os.path.join(RELAX_PATH, 'issue.relax.xml')

##################
## Test classes ##
##################
class TestLicense(TestApi):

    def test_invalid_class(self):
        """An invalid license class name should return an explicit error."""
        res = self.app.get('/license/noclass')
        assert relax_validate(RELAX_ERROR, res.body)

    def test_license_class_structure(self):
        """Test that each license class returns a valid XML chunk."""
        for lclass in self.data.license_classes():
            res = self.app.get('/license/%s' % lclass)
            assert relax_validate(RELAX_LICENSECLASS, res.body)

    def test_default_locale(self):
        """/license default locale."""
        for lclass in self.data.license_classes():
            default = self.app.get('/license/%s' % lclass).body
            explicit = self.app.get('/license/%s?locale=en' % lclass).body
            assert default == explicit

    def test_locales(self):
        """Try each license class with different locales."""
        for lclass in self.data.license_classes():
            for locale in self.data.locales():
                res = self.app.get('/license/%s?locale=%s' % (lclass, locale))
                assert relax_validate(RELAX_LICENSECLASS, res.body)

    def test_identical_xml(self):
        """Get and license return identical xml."""
        for lclass in self.data.license_classes():
            for answers, query_string in zip(
                           self.data.xml_answers(lclass),
                           self.data.query_string_answers(lclass)
                           ):
                issue = self.app.post('/license/%s/issue' % lclass,
                                      params={'answers':answers}).body
                get = self.app.get('/license/%s/get%s' %
                                     (lclass, query_string)).body
                assert get == issue

    def test_extra_args(self):
        """/license extra nonsense arguments."""
        for lclass in self.data.license_classes():
            extra = self.app.get('/license/%s?foo=bar' % lclass).body
            normal = self.app.get('/license/%s' % lclass).body
            assert extra == normal
            assert relax_validate(RELAX_LICENSECLASS, extra)


class TestLicenseIssue(TestApi):
    """Tests for /license/<class>/issue. Called with HTTP POST."""

    ''' NOTE: test fails under CherryPy implementation, but should pass
    def test_invalid_class(self):
        """/issue should return an error with an invalid class."""
        answers = '<answers><locale>en</locale><license-standard>' + \
                  '<commercial>y</commercial>' + \
                  '<derivatives>y</derivatives>' + \
                  '<jurisdiction></jurisdiction>' + \
                  '</license-standard></answers>'
        res = self.app.post('/license/blarf/issue',
                                params={'answers':answers})
        assert relax_validate(RELAX_ERROR, res.body)
    '''

    def test_empty_answer_error(self):
        """Issue with no answers or empty answers should return an error."""
        res = self.app.post('/license/blarf/issue')
        assert relax_validate(RELAX_ERROR, res.body)

    def test_invalid_answers(self):
        """Invalid answer string returns error."""
        res = self.app.post('/license/standard/issue',
                                params={'answers':'<foo/>'})
        assert relax_validate(RELAX_ERROR, res.body)

    def _issue(self, lclass):
        """Common /issue testing code."""
        for answers in self.data.xml_answers(lclass):
            res = self.app.post('/license/%s/issue' % lclass,
                                     params={'answers':answers})
            print 'lclass: %s' % lclass
            print 'answers: %s' % answers
            print
            assert relax_validate(RELAX_ISSUE, res.body)

    def test_license_standard(self):
        """/issue issues standard licenses successfully."""
        self._issue('standard')

    def test_license_publicdomain(self):
        """/issue issues publicdomain licenses successfully."""
        self._issue('publicdomain')

    def test_license_zero(self):
        """/issue issues zero licenses successfully."""
        self._issue('zero')

    def test_license_recombo(self):
        """/issue issues recombo licenses successfully."""
        self._issue('recombo')

    def test_publicdomain_failure(self): 
        """publicdomain fails with certain answers."""
        answers = '<answers><locale>en</locale><license-publicdomain>' + \
                  '<commercial>y</commercial>' + \
                  '<derivatives>y</derivatives>' + \
                  '<jurisdiction></jurisdiction>' + \
                  '</license-publicdomain></answers>'
        res = self.app.post('/license/publicdomain/issue',
                                params={'answers':answers})
        assert relax_validate(RELAX_ERROR, res.body)

    def test_recombo_failure(self):
        """recombo fails with certain answers."""
        answers = '<answers><locale>en</locale><license-publicdomain>' + \
                  '<commercial>y</commercial>' + \
                  '<derivatives>y</derivatives>' + \
                  '<jurisdiction></jurisdiction>' + \
                  '</license-publicdomain></answers>'
        res = self.app.post('/license/recombo/issue',
                                params={'answers':answers})
        assert relax_validate(RELAX_ERROR, res.body)


class TestLicenseGet(TestApi):

    def test_invalid_class(self):
        """/get should return an error with an invalid class."""
        res = self.app.get('/license/%s/get' % hash(self))
        assert relax_validate(RELAX_ERROR, res.body)

    def test_ignore_extra_args(self):
        """Test /get ignores extra nonsense arguments."""
        for lclass in self.data.license_classes():
            for query_string in self.data.query_string_answers(lclass):
                res = self.app.get('/license/%s/get%s&foo=bar' %
                                         (lclass, query_string))
                assert relax_validate(RELAX_ISSUE, res.body)

    def _get(self, lclass):
        """Common /get testing code."""
        for query_string in self.data.query_string_answers(lclass):
            res = self.app.get('/license/%s/get%s' %
                                     (lclass, query_string))
            print 'lclass: %s' % lclass
            print 'query_string: %s' % query_string
            print
            assert relax_validate(RELAX_ISSUE, res.body)

    def test_license_standard(self):
        """/get issues standard licenses successfully."""
        self._get('standard')

    def test_license_publicdomain(self):
        """/get issues publicdomain licenses successfully."""
        self._get('publicdomain')

    def test_license_recombo(self):
        """/get issues recombo licenses successfully."""
        self._get('recombo')

    def test_license_zero(self):
        """/get issues recombo licenses successfully."""
        self._get('zero')
