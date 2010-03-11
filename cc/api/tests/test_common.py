
import lxml
import lxml.etree
from StringIO import StringIO
import os
import operator
import random

import webtest

import cc.api.app

import web
web.config.debug = False

##################
## Public names ##
##################
__all__ = (
           'RELAX_PATH',
           'relax_validate',
           'TestApi',
          )

###############
## Constants ##
###############
RELAX_PATH = os.path.join(os.path.dirname(__file__), 'schemata')

TOO_MANY = 25

#######################
## Utility functions ##
#######################
def relax_validate(schema_filename, instance_buffer):
    """Validates xml string instance_buffer against RelaxNG schema 
       located in file schema_filename. By convention, schema_filename 
       is a constant defined in the test module. Schema files are 
       located in tests/schemata."""

    relaxng = lxml.etree.RelaxNG(lxml.etree.parse(schema_filename))
    instance = lxml.etree.parse(StringIO(instance_buffer))

    if not relaxng.validate(instance):
        print relaxng.error_log.last_error
        return False
    else:
        return True

#####################
## Utility classes ##
#####################
class TestData:
    """Generates test data for use in exercising the CC API."""

    def __init__(self):
        """Configure app to query CC API. This is for using live,
           rather than canned, data."""
        
        self.app = webtest.TestApp(cc.api.app.application.wsgifunc())
        
    def _permute(self, lists): #TODO: document function
        if lists:
            result = map(lambda i: (i,), lists[0])
            for list in lists[1:]:
                curr = []
                for item in list:
                    new = map(operator.add, result, [(item,)]*len(result))
                    curr[len(curr):] = new
                result = curr
        else:
            result = []
        return result

    def license_classes(self):
        return ['standard', 'publicdomain', 'recombo', 'zero']

    def _field_enums(self, lclass):
        """Retrieve the license information for this class, and generate 
           a set of answers for use with testing."""
        enums = [('jurisdiction', ['', 'us', 'de', 'uk'])]
        if lclass in ['publicdomain', 'zero']:
            return enums
        elif lclass == 'recombo':
            enums.append(('sampling',
                          ['sampling','samplingplus','ncsamplingplus']))
            return enums
        else:
            enums.append(('commercial', ['y', 'n']))
            enums.append(('derivatives', ['y', 'sa', 'n']))
            return enums

    def locales(self, canned=True):
        """Return a list of supported locales.
        Can return canned data, or the list of locales that
        /locales returns."""
        locales = None
        if canned:
            locales = [
                        'en', # English
                        'de', # German
                        # 'he', # Hebrew TODO: fix html rtl formatting
                        'el', # Greek
                      ]
        else:
            res = app.get('/locales')
            locale_doc = lxml.etree.parse(StringIO(res.body))
            locales = [n for n in locale_doc.xpath('//locale/@id')
                                              if n not in ('he',)]
        return locales

    def params(self, lclass, canned=True):
        all_params = []
        all_answers = self._field_enums(lclass)
        all_locales = self.locales(canned)
        for ans_combo in self._permute([n[1] for n in all_answers]):
            for locale in all_locales:
                params = zip([n[0] for n in all_answers], ans_combo)
                params.append(('locale', locale))
                all_params.append(params)
        # thin out param list if there are too many
        if len(all_params) > TOO_MANY:
            r = random.Random(42) # deterministic b/c seeded w/ constant
            all_params = r.sample(all_params, TOO_MANY)
        return all_params

    # TODO: fix hackery
    # TODO: should rely on cc.license from here on....!!!
    def xml_answers(self, lclass):
        all_params = self.params(lclass)
        for params in all_params:
            answers_xml = lxml.etree.Element('answers')
            locale_node = lxml.etree.SubElement(answers_xml, 'locale')
            locale_node.text = [n[1] for n in params if n[0]=='locale'][0]
            class_node = lxml.etree.SubElement(answers_xml, 'license-%s' % lclass)
            for a in [n for n in params if n[0]!='locale']:
                a_node = lxml.etree.SubElement(class_node, a[0])
                a_node.text = a[1]
            yield lxml.etree.tostring(answers_xml)

    def query_string_answers(self, lclass):
        all_params = self.params(lclass)
        for params in all_params:
            param_strs = ['='.join(n) for n in params]
            result = '?' + '&'.join(param_strs)
            yield result


##########################
## Base class for tests ##
##########################
class TestApi:
    """Base class of test classes for the CC API. Defines test fixture
       behavior for creating and destroying webtest.TestApp instance of 
       the WSGI server."""

    def setUp(self):
        """Test fixture for nosetests:
           - sets up the WSGI app server
           - creates test data generator"""
        self.app = webtest.TestApp(cc.api.app.application.wsgifunc())
        self.data = TestData()
        
    def tearDown(self):
        """Test fixture for nosetests:
           - tears down the WSGI app server"""
        pass

    def makexml(self, bodystr):
        """Wraps text in a root element and escapes some special characters
           so as to make non-conforming HTML into XML."""
        retval = bodystr.replace('&', '&amp;') # makes the xml parser choke
        retval = '<root>' + retval + '</root>' # b/c it's not valid xml
        return retval

