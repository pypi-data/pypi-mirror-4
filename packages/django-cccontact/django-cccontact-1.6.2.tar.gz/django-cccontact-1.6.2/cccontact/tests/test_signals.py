from django.test import TestCase
from django.core.urlresolvers import reverse
from cccontact.tests.mock import MockRequest
from cccontact.views import contact
from cccontact.signals import contact_form_is_valid

testdict = {}

class SignalTestCases(TestCase):

    def setUp(self):
        # set up test dict
        global testdict
        testdict = {'signal_sent': False}
        # set up request factory
        self.rf = MockRequest()
        # set up the data
        data = {
                'name': 'Tester',
                'subject': 'I want to buy',
                'email': 'customer@customer.com',
                'phone': '9789789',
                'm': 'I want to buy all the things'}
        # make the request
        self.request = self.rf.post(
                reverse('cccontact:contact'),
                data)

    def tearDown(self):
        # disconnect signals
        contact_form_is_valid.disconnect(
                dispatch_uid='test_contact_form_is_valid_sends')
        contact_form_is_valid.disconnect(
                dispatch_uid='test_sends_correct_arguments')

    def test_sends_correct_arguments(self):
        """"test that the view passes the signal the correct args"""
        global testdict
        # the listener
        def test_listener(sender, request, form, **kwargs):
            global testdict
            testdict['request'] = request
            testdict['form'] = form
        # connect it
        contact_form_is_valid.connect(
                test_listener,
                dispatch_uid='test_sends_correct_arguments')
        # now get the response
        response = contact(self.request)
        # test dict has been updated
        self.assertTrue(testdict['request'], True)
        self.assertTrue(testdict['form'], True)

    def test_contact_form_is_valid_sends(self):
        """when the contact form is valid the valid signal is sent"""
        # our test dict confirms that the signal not sent
        global testdict
        self.assertEqual(testdict['signal_sent'], False)
        # test listener
        def test_listener(**kwargs):
            global testdict
            testdict['signal_sent'] = True
        # connect it
        contact_form_is_valid.connect(
                test_listener,
                dispatch_uid='test_contact_form_is_valid_sends')
        # now get the response
        response = contact(self.request)
        # test dict has been updated
        self.assertEqual(testdict['signal_sent'], True)
