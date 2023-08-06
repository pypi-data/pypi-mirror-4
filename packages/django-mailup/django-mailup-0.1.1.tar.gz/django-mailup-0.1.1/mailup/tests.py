"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from mailup.webservice import MailUpHttp
from mailup import settings

class MailupTest(TestCase):
    def check_settings(self):
        self.assertNotEqual(settings.MAILUP_TEST_GUID, '', "Set MAILUP_TEST_GUID settings")
        self.assertNotEqual(settings.MAILUP_TEST_ID_LIST, '', "Set MAILUP_TEST_ID_LIST settings")
        self.assertNotEqual(settings.MAILUP_TEST_ID_GROUP, '', "Set MAILUP_TEST_ID_GROUP settings")
        self.assertNotEqual(settings.MAILUP_TEST_EMAIL, '', "Set MAILUP_TEST_EMAIL settings")

    def test_subscribe_user(self):
        self.check_settings()
        retcode = MailUpHttp.subscribeUser(settings.MAILUP_TEST_ID_LIST, settings.MAILUP_TEST_GUID, settings.MAILUP_TEST_EMAIL, settings.MAILUP_TEST_ID_GROUP)
        self.assertNotIn(retcode, ['-1011', '1'])

    def test_unsubscribe_user(self):
        self.check_settings()
        retcode = MailUpHttp.unsubscribeUser(settings.MAILUP_TEST_ID_LIST, settings.MAILUP_TEST_GUID, settings.MAILUP_TEST_EMAIL)
        self.assertNotIn(retcode, ['-1011', '1'])

    def test_check_subscriber(self):
        self.check_settings()
        retcode = MailUpHttp.checkSubscriber(settings.MAILUP_TEST_ID_LIST, settings.MAILUP_TEST_GUID, settings.MAILUP_TEST_EMAIL)
        self.assertNotEqual(retcode, '-1011')
