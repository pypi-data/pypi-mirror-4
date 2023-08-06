# -*- coding: utf-8 -*-

# NOTE: A models.py file must exist, even if empty, or the test suite
# will not run! See django/django#7198.

# Usage examples:
#
#   manage.py test django_saltapi
#   manage.py test django_saltapi.testPing
#   manage.py test -v 3 django_saltapi

# Import python libs
import os
import sys
import re
import json

# Import 3rd party libs
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.simple import DjangoTestSuiteRunner
from django.utils import unittest
from mock import MagicMock, patch
import salt.client


CONFIG = {'API_ROOT_URL': 'http://salt/api/salt/',
          'VALID_TARGETS': ['salt'],
          'INVALID_TARGETS': ['nonexist']}

for (k, v) in CONFIG.iteritems():
    if k in os.environ:
        if re.match('.+ .+', os.environ[k]):
            setattr(sys.modules[__name__], k, os.environ[k].split(' '))
        elif re.match('\d+', os.environ[k]):
            setattr(sys.modules[__name__], k, int(os.environ[k]))
        else:
            setattr(sys.modules[__name__], k, os.environ[k])
    else:
        setattr(sys.modules[__name__], k, v)

# TODO: remove in favor of iteration over VALID_TARGETS
SINGLE_TARGET = u'salt'


class NoDatabaseTestRunner(DjangoTestSuiteRunner):
    '''
    A test runner to test without database creation.

    Add this to your `settings.py`::

      TEST_RUNNER = 'django_saltapi.tests.NoDbTestRunner'
    '''

    def setup_databases(self, **kwargs):
        '''
        Override the database creation defined in parent class.
        '''
        pass

    def teardown_databases(self, old_config, **kwargs):
        '''
        Override the database teardown defined in parent class.
        '''
        pass


class testPing(TestCase):
    # TODO: this test should iterate over VALID_TARGETS
    @patch.object(salt.client.LocalClient, 'cmd')
    def test_ping(self, mock):
        mock.return_value = {}
        r = self.client.get(reverse(
                'django_saltapi.views.ping',
                kwargs={'tgt': SINGLE_TARGET}))
        mock.assert_called_with(
            SINGLE_TARGET,
            'test.ping',
            ret='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')


class testMinions(TestCase):
    @patch.object(salt.client.LocalClient, 'cmd')
    def test_list_minions(self, mock):
        mock.return_value = {'foo': {'nodename': 'foo'},
                             'bar': {'nodename': 'bar'}}
        r = self.client.get(reverse('django_saltapi.views.minions'))
        mock.assert_called_with(
            '*',
            'grains.items',
            ret='json'
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        data = json.loads(r.content)
        self.assertTrue('foo' in data.keys())
        self.assertTrue('foo' in data['foo']['nodename'])

    # TODO: this test should iterate over VALID_TARGETS
    @patch.object(salt.client.LocalClient, 'cmd')
    def test_minions(self, mock):
        mock.return_value = {SINGLE_TARGET: {'nodename': SINGLE_TARGET}}
        r = self.client.get(reverse('django_saltapi.views.minions',
                                    kwargs={'mid': SINGLE_TARGET}))
        mock.assert_called_with(
            SINGLE_TARGET,
            'grains.items',
            ret='json'
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        data = json.loads(r.content)
        self.assertTrue(SINGLE_TARGET in data.keys())
        self.assertTrue(SINGLE_TARGET in data[SINGLE_TARGET]['nodename'])


class testJobs(TestCase):
    @patch.object(salt.client.LocalClient, 'cmd')
    def test_list_jobs(self, mock):
        r = self.client.get(reverse('django_saltapi.views.jobs'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        self.assertTrue(re.match('\d+', json.loads(r.content).keys()[0]))

    @unittest.skip("not implemented yet")
    def test_lookup_jid(self):
        pass

    @unittest.skip("does not return 404 yet")
    def test_lookup_invalid_jid(self):
        r = self.client.get(reverse('django_saltapi.views.jobs',
                                    kwargs={'jid': '20999999999999999999'}))
        self.assertEqual(r.status_code, 404)


class testApi(TestCase):
    def test_index(self):
        r = self.client.get(reverse('django_saltapi.views.apiwrapper'))
        self.assertEqual(r.status_code, 200)

    def test_non_existant(self):
        r = self.client.get(
            reverse('django_saltapi.views.apiwrapper') + 'boogeyman')
        self.assertEqual(r.status_code, 404)

    # TODO: this test should iterate over VALID_TARGETS
    @patch.object(salt.client.LocalClient, 'cmd')
    def test_test_ping(self, mock):
        mock.return_value = {SINGLE_TARGET: True}
        r = self.client.post(reverse('django_saltapi.views.apiwrapper'),
                             {'client': 'local',
                              'tgt': SINGLE_TARGET,
                              'fun': 'test.ping',
                              'arg': [],
                              })
        mock.assert_called_with(
            client=u'local',
            tgt=SINGLE_TARGET,
            fun=u'test.ping',
            arg=u''
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        data = json.loads(r.content)
        self.assertTrue(SINGLE_TARGET in data.keys())
        self.assertTrue(data[SINGLE_TARGET])

    # TODO: this test should iterate over VALID_TARGETS
    @patch.object(salt.client.LocalClient, 'cmd')
    def test_status_uptime(self, mock):
        mock.return_value = {SINGLE_TARGET: '17:44pm  up 1 day 17:03,  5 users,  load average: 0.12, 0.08, 0.06'}
        r = self.client.post(reverse('django_saltapi.views.apiwrapper'),
                             {'client': 'local',
                              'tgt': SINGLE_TARGET,
                              'fun': 'status.uptime',
                              'arg': [],
                              })
        mock.assert_called_with(
            client=u'local',
            tgt=SINGLE_TARGET,
            fun=u'status.uptime',
            arg=u''
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        data = json.loads(r.content)
        self.assertTrue(SINGLE_TARGET in data.keys())
        self.assertTrue(re.match('.+up \d+ day.+', data[SINGLE_TARGET]))
