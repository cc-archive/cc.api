
import os
from urllib import urlencode
import itertools

from cc.api.tests.test_common import *

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
                assert get == issue, "%s %s" % (answers, query_string)

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
        res = self.app.post('/license/standard/issue')
        assert relax_validate(RELAX_ERROR, res.body)

    def test_invalid_answers(self):
        """Invalid answer string returns error."""
        res = self.app.post('/license/standard/issue',
                                params={'answers':'<foo/>'})
        assert relax_validate(RELAX_ERROR, res.body)
        res = self.app.post('/license/standard/issue',
                                params={'answers':'<answers><locale>en</loca'})
        assert relax_validate(RELAX_ERROR, res.body)

    def _issue(self, lclass):
        """Common /issue testing code."""
        for answers in self.data.xml_answers(lclass):
            print 'lclass: %s' % lclass
            print 'answers: %s' % answers
            print
            res = self.app.post('/license/%s/issue' % lclass,
                                     params={'answers':answers})
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

    def test_software_failure(self):
        answers = "<answers><locale>en</locale><license-software /></answers>"
        res = self.app.post('/license/software/issue', params={'answers':answers})
        assert relax_validate(RELAX_ERROR, res.body)
        
class TestLicenseWorkInfo(TestApi):

    _fields = {
        'title': 'Testing Title',
        'attribution_url': 'http://example.com/work-url',
        'source-url': 'http://example.com/source-url',
        'type': 'Text',
        'more_permissions_url': 'http://example.com/more-permissions-url',
        }        
    _cc0_fields = {
        'title': 'Testing Title',
        'actor_href': 'http://example.com',
        'name': 'Testing',
        'territory': 'US',
        }

    _answers = '<answers><locale>en</locale><license-standard>' + \
              '<commercial>y</commercial>' + \
              '<derivatives>y</derivatives>' + \
              '<jurisdiction></jurisdiction>' + \
              '</license-standard>%s</answers>'
    
    _cc0_answers = '<answers><license-zero />%s</answers>'
    
    def _work_info_string(self, fields):
        root = "<work-info>"
        for k,v in fields.items():
            root += "<%(key)s>%(value)s</%(key)s>" % {'key':k,'value':v}
        root += "</work-info>"
        return root

    def _permute_workinfo(self, fields, values=None):
        if values == None:
            values = self._fields
        work_infos = []
        for i in range(1, len(fields) + 1):
            for c in itertools.combinations(fields, i):
                workfields = dict([ (f, values[f]) for f in c])
                work_infos.append(workfields)
        return work_infos

    def test_license_workinfo(self):
        """ get & issue should return identical (and valid) responses based on the
        data provided in work-info. """

        work_infos = self._permute_workinfo(self._fields.keys())
        
        for workinfo in work_infos:
            wi = self._work_info_string(
                dict([ (f, self._fields[f]) for f in workinfo ]))
            i = self.app.post('/license/standard/issue',
                              params={'answers':self._answers % wi})
            g = self.app.get('/license/standard/get?' + urlencode(workinfo))
            
            for f in workinfo:
                # assert field is present in issue response
                assert self._fields[f] in i.body, '%s=%s not in issue results.' % \
                       (f, self._fields[f])
                # assert field is present in get response
                assert self._fields[f] in g.body, '%s=%s not in get results.' % \
                       (f, self._fields[f])
                # issue and get should be identical
                assert i.body == g.body
                
        work_infos = self._permute_workinfo(self._cc0_fields.keys(), self._cc0_fields)
        for workinfo in work_infos:
            wi = self._work_info_string(
                dict([ (f, self._cc0_fields[f]) for f in workinfo ]))
            i = self.app.post('/license/zero/issue',
                              params={'answers':self._cc0_answers % wi})
            g = self.app.get('/license/zero/get?' + urlencode(workinfo))
            for f in workinfo:
                # assert field is present in issue response
                assert self._cc0_fields[f] in i.body, '%s=%s not in issue results.'% \
                       (f, self._cc0_fields[f])
                # assert field is present in get response
                assert self._cc0_fields[f] in g.body, '%s=%s not in get results.' % \
                       (f, self._cc0_fields[f])
                # issue and get should be identical
                assert i.body == g.body

    def test_invalid_work_jurisdiction(self):
        """ cc.license will KeyError when an invalid work_jurisidction is passed to
        the CC0 formatter. """
        res = self.app.get('/license/zero/get?territory=PUKE')
        assert relax_validate(RELAX_ERROR, res.body)
        res = self.app.post('/license/zero/issue',
                            params={'answers': self._cc0_answers % (
                                    '<work-info><territory>' + \
                                    'PUKE</territory></work-info>')})
        assert relax_validate(RELAX_ERROR, res.body)

class TestLicenseGet(TestApi):
    
    def test_invalid_class(self):
        """/get should return an error with an invalid class."""
        res = self.app.get('/license/%s/get' % hash(self))
        assert relax_validate(RELAX_ERROR, res.body)

    def test_software_is_invalid_class(self):
        """/get should return an error with an invalid class."""
        res = self.app.get('/license/software/get')
        assert relax_validate(RELAX_ERROR, res.body)

    def test_invalid_answers(self):
        """/get should return an error for invalid answers."""
        res = self.app.get('/license/standard/get?commercial=z')
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
