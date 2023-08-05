from django.test import TestCase
from django.core.urlresolvers import reverse
from cccontact.tests.mock import MockRequest
from cccontact.views import contact, complete
from mailer.models import Message

class ViewTestCases(TestCase):

    def setUp(self):
        self.rf = MockRequest()

    def test_complete_200(self):
        """The complete page renders with 200 response"""
        request = self.rf.get(reverse('cccontact:complete'))
        response = complete(request)
        self.assertEqual(200, response.status_code)

    def test_contact_200__get(self):
        """The contact view gives a 200 status"""
        request = self.rf.get(reverse('cccontact:contact'))
        response = contact(request)
        self.assertEqual(200, response.status_code)

    def test_contact_200_post(self):
        """The contact view gives a 200 status"""
        request = self.rf.post(
                reverse('cccontact:contact'),
                {})
        response = contact(request)
        self.assertEqual(200, response.status_code)

    def test_contact_honeypot(self):
        """if data is entered into the honeypot then abort,
        but do so silently and return a 200"""
        self.assertEqual(0, Message.objects.count())
        # send data including honeypot
        data = {
                'name': 'Tester',
                'subject': 'Oh HAI',
                'email': 'spammer@spam.com',
                'message': 'buy viagra',
                'phone': '9789789',
                'm': 'buy viagra'}
        request = self.rf.post(
                reverse('cccontact:contact'),
                data)
        response = contact(request)
        # 200 response
        self.assertEqual(200, response.status_code)
        # no messages
        self.assertEqual(0, Message.objects.count())


    def test_send(self):
        """if the correcy data is sent, then a message is sent"""
        self.assertEqual(0, Message.objects.count())
        # send data including honeypot
        data = {
                'name': 'Tester',
                'subject': 'I want to buy',
                'email': 'customer@customer.com',
                'phone': '9789789',
                'm': 'I want to buy all the things'}
        request = self.rf.post(
                reverse('cccontact:contact'),
                data)
        response = contact(request)
        # 200 response
        self.assertEqual(302, response.status_code)
        # no messages
        self.assertEqual(1, Message.objects.count())
