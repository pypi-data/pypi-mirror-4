from django.test import TestCase
from django.core.urlresolvers import reverse
from mailer.models import Message
from cccontact.tests.mock import MockRequest
from cccontact.views import contact
from cccontact.signals import contact_form_is_valid



class ListenerTestCases(TestCase):


    def setUp(self):
        # set up request factory
        self.rf = MockRequest()

    def test_badheadererror_subject(self):
        """BadHeaderError are handled gracefully"""
        # none
        self.assertEqual(0, Message.objects.count())
        # set up
        data = {
                'name': 'Tester',
                'subject': 'I want to buy\n\n\ncc:a@a.com',
                'email': 'customer@customer.com',
                'phone': '9789789',
                'm': 'I want to buy all the things'}
        # post it
        request = self.rf.post(
                reverse('cccontact:contact'),
                data)
        # get response
        response = contact(request)
        # now have one
        self.assertEqual(1, Message.objects.count())
