from django.test import TestCase
from django.conf import settings
from cccontact import settings as c_settings

# ------------------------ FAKES
class FakeForm(object):
    """Does nothing. Used in the testcases"""


#------------------------ TEST CASES
class SettingTestCases(TestCase):

    def setUp(self):
        reload(c_settings)

    def tearDown(self):
        try:
            del(settings.CCCONTACT_MODEL)
        except AttributeError:
            pass
        try:
            del(settings.CCCONTACT_FORM)
        except AttributeError:
            pass


    def test_default_form(self):
        """The cccontact.forms.ContactForm form is the default form"""
        self.assertEqual(
                c_settings.FORM.__name__,
                'ContactForm')

    def test_custom_form(self):
        """The custom form can be overridden"""
        # set thesettings.CCCONTACT_FORM custom form
        settings.CCCONTACT_FORM = 'cccontact.tests.test_settings.FakeForm'
        reload(c_settings)
        # we have the fake form
        self.assertEqual('FakeForm', c_settings.FORM.__name__)
