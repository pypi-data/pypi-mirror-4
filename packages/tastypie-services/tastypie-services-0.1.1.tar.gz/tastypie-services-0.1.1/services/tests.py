import json

from django.conf import settings

minimal = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'mydatabase'
        }
    },
    'ROOT_URLCONF': ''
}

if not settings.configured:
    settings.configure(**minimal)

from django.test import TestCase

from mock import patch
from nose.tools import eq_


@patch.object(settings, 'DEBUG', False)
class TestStatus(TestCase):
    urls = 'services.test_urls'

    def setUp(self):
        self.api_name = 'services'
        self.list_url = '/services/status/'

    def test_working_status(self):
        with self.settings(SERVICES_STATUS_MODULE='services.status_test'):
            res = self.client.get(self.list_url)
            eq_(res.status_code, 200)

    def failed(self, res, on):
        eq_(res.status_code, 500)
        data = json.loads(res.content)
        assert '%s: False' % on in data['error_message'], data


@patch.object(settings, 'DEBUG', False)
class TestError(TestCase):
    urls = 'services.test_urls'

    def setUp(self):
        self.api_name = 'services'
        self.list_url = '/services/error/'

    def test_throws_error(self):
        res = self.client.get(self.list_url)
        eq_(res.status_code, 500)
