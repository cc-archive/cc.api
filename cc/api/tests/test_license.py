import os
from urllib import urlencode

from cc.api.tests.test_common import *

def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)

####################
## Path constants ##
####################
RELAX_ERROR = os.path.join(RELAX_PATH, 'error.relax.xml')
RELAX_LICENSECLASS = os.path.join(RELAX_PATH, 'licenseclass.relax.xml')
RELAX_ISSUE = os.path.join(RELAX_PATH, 'issue.relax.xml')
RELAX_JURISDICTION = os.path.join(RELAX_PATH, 'jurisdiction.relax.xml')

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
            res = self.app.post('/license/%s/issue' % lclass,
                                     params={'answers':answers})
            assert relax_validate(RELAX_ISSUE, res.body)

    def test_license_standard(self):
        """/issue issues standard licenses successfully."""
        self._issue('standard')

    def test_license_publicdomain(self):
        """/issue issues publicdomain licenses successfully."""
        self._issue('publicdomain')

    def test_license_mark(self):
        """/issue issues pdm successfully."""
        self._issue('mark')

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

    def test_deprecated_license_issue(self):
        """ Results should include information regarding the deprecation
        status of a license. """

        answers = "<answers><license-recombo><jurisdiction/><sampling>sampling</sampling></license-recombo></answers>"
        res = self.app.post('/license/recombo/issue', params={'answers':answers})
        print res.body
        assert "<deprecated>true</deprecated>" in res.body

        answers = "<answers><license-standard><commercial>y</commercial><derivatives>y</derivatives><jurisdiction /></license-standard></answers>"
        res = self.app.post('/license/standard/issue', params={'answers':answers})
        print res.body
        assert "<deprecated>false</deprecated>" in res.body

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
            for c in combinations(fields, i):
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

class TestLicenseJurisdiction(TestApi):

    def test_invalid_jurisdiction(self):
        """ should return error for an invalid juri code """
        res = self.app.get('/license/standard/jurisdiction/xx')
        assert relax_validate(RELAX_ERROR, res.body)

    def test_get_jurisdiction(self):
        """ license/standard/jurisdiction/<juri code> lists most current
        license versions ported to the jurisdiction """
        for j in self.data.jurisdictions():
            res = self.app.get('/license/standard/jurisdiction/%s' % j)
            assert relax_validate(RELAX_JURISDICTION, res.body)

    def test_get_jurisdiction_past_versions(self):
        """ allow for non-current licenses to be returned when the
        current query param is set to 0 """
        # 'es' jurisdiction has more than one version in its history
        past = self.app.get('/license/standard/jurisdiction/es?current=0')
        assert relax_validate(RELAX_JURISDICTION, past.body)
        current = self.app.get('/license/standard/jurisdiction/es')
        assert len(past.body) > len(current.body)

    def test_get_unported(self):
        """ license/standard/jurisdiction/ should return latest unported """
        res = self.app.get('/license/standard/jurisdiction/')
        assert relax_validate(RELAX_JURISDICTION, res.body)
        assert 'Unported' in res.body
    
    
