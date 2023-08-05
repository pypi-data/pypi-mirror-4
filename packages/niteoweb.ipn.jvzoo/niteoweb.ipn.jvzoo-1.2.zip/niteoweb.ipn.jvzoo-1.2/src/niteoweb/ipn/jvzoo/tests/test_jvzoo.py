# -*- coding: utf-8 -*-
"""Test all aspects of the @@jvzoo view."""

from niteoweb.ipn.jvzoo.testing import IntegrationTestCase
from plone import api
from zope.testing.loggingsupport import InstalledHandler

import mock

log = InstalledHandler('niteoweb.ipn.jvzoo')

KEY_RECORD = 'niteoweb.ipn.jvzoo.interfaces.IJVZooSettings.secretkey'


class TestJVZoo(IntegrationTestCase):
    """Test runtime flow through @@jvzoo."""

    def setUp(self):
        """Prepare testing environment."""
        self.portal = self.layer['portal']
        self.view = self.portal.restrictedTraverse('jvzoo')

        # create test group
        api.group.create(groupname='ipn_1')
        group = api.group.get(groupname='ipn_1')
        group.setGroupProperties(mapping={'validity': 31})

    def tearDown(self):
        """Clean up after yourself."""
        log.clear()

    def _assert_log_record(self, level, user, msg):
        """Utility method for testing log output."""
        self.assertEqual(log.records[0].name, 'niteoweb.ipn.jvzoo')
        self.assertEqual(log.records[0].levelname, level)
        self.assertEqual(log.records[0].getMessage(), "{0}: {1}".format(
            user, msg))
        log.records.pop(0)

    def test_call_with_no_POST(self):
        """Test @@jvzoo's response when POST is empty."""
        html = self.view()
        self.failUnless('No POST request.' in html)
        self._assert_log_record('WARNING', 'test_user_1_', "No POST request.")

    def test_call_with_missing_parameter(self):
        """Test @@jvzoo's response when POST is missing a parameter."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(foo='bar')

        # set secretkey
        api.portal.set_registry_record(KEY_RECORD, u'secret')

        # test html
        html = self.view()
        self.assertEqual(html, "POST parameter missing: 'cverify'")

        # test log output
        self.assertEqual(len(log.records), 1)
        self._assert_log_record(
            'WARNING',
            'test_user_1_',
            "POST parameter missing: 'cverify'",
        )

    def test_call_with_missing_secret_key(self):
        """Test @@jvzoo's response when JVZoo secret-key is not set."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(foo='bar')

        # test html
        html = self.view()
        self.assertEqual(
            html, "POST handling failed: JVZoo secret-key is not set.")

        # test log output
        self.assertEqual(len(log.records), 1)
        self._assert_log_record(
            'WARNING',
            'test_user_1_',
            "POST handling failed: JVZoo secret-key is not set.",
        )

    @mock.patch('niteoweb.ipn.jvzoo.jvzoo.JVZoo._verify_POST')
    def test_call_with_invalid_checksum(self, verify_post):
        """Test @@jvzoo's response when checksum cannot be verified."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(foo='bar')

        # mock return from _verify_POST
        verify_post.side_effect = AssertionError

        # test html
        html = self.view()
        self.assertEqual(html, 'Checksum verification failed.')

        # test log output
        self.assertEqual(len(log.records), 1)
        self._assert_log_record(
            'WARNING',
            'test_user_1_',
            "Checksum verification failed.",
        )

    @mock.patch('niteoweb.ipn.jvzoo.jvzoo.JVZoo._verify_POST')
    def test_call_with_internal_exception(self, verify_post):
        """Test @@jvzoo's response when there is an internal problem."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(foo='bar')

        # mock return from _verify_POST
        verify_post.side_effect = Exception('Internal foo.')

        # test html
        html = self.view()
        self.assertEqual(html, 'POST handling failed: Internal foo.')

        # test log output
        self.assertEqual(len(log.records), 1)
        self._assert_log_record(
            'WARNING',
            'test_user_1_',
            "POST handling failed: Internal foo.",
        )

    @mock.patch('niteoweb.ipn.jvzoo.jvzoo.JVZoo._verify_POST')
    @mock.patch('niteoweb.ipn.jvzoo.jvzoo.JVZoo._parse_POST')
    def test_call_with_valid_POST(self, parse_post, verify_post):
        """Test @@jvzoo's response when POST is valid."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(value='non empty value')

        # mock post handling
        verify_post.return_value = True
        parse_post.return_value = dict(
            email='new@test.com',
            product_id='1',
            trans_type='SALE',
            fullname='New Member',
            affiliate='aff@test.com'
        )

        # test html output
        self.assertEqual('Done.', self.view.render())

        # test log output
        self.assertEqual(len(log.records), 2)

        self._assert_log_record(
            'INFO',
            'test_user_1_',
            "POST successfully parsed for 'new@test.com'.",
        )

        self._assert_log_record(
            'INFO',
            'test_user_1_',
            "Calling 'enable_member' in niteoweb.ipn.core.",
        )


class TestTransactionTypesToActionsMapping(TestJVZoo):
    """Test how Transaction Types map to niteoweb.ipn.core actions."""

    @mock.patch('niteoweb.ipn.jvzoo.jvzoo.getAdapter')
    @mock.patch('niteoweb.ipn.jvzoo.jvzoo.JVZoo._verify_POST')
    @mock.patch('niteoweb.ipn.jvzoo.jvzoo.JVZoo._parse_POST')
    def _simulate_transaction(
        self,
        parse_post,
        verify_post,
        getAdapter,
        trans_type=None
    ):
        """Simulate a transaction of a certain type from JVZoo."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(value='non empty value')

        # mock methods
        verify_post.return_value = True
        parse_post.return_value = dict(
            email='new@test.com',
            product_id='1',
            trans_type=trans_type,
        )
        getAdapter.return_value.enable_member.return_value = 'foo'
        getAdapter.return_value.disable_member.return_value = 'bar'

        html = self.view()
        self.assertEqual('Done.', html)

        # 1. post parsed, 2. action called
        self.assertEqual(len(log.records), 2)

    def test_SALE(self):
        """Test SALE Transaction Type."""
        self._simulate_transaction(trans_type='SALE')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(
            msg, "test_user_1_: Calling 'enable_member' in niteoweb.ipn.core.")

    def test_BILL(self):
        """Test BILL Transaction Type."""
        self._simulate_transaction(trans_type='BILL')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(
            msg, "test_user_1_: Calling 'enable_member' in niteoweb.ipn.core.")

    def test_RFND(self):
        """Test RFND Transaction Type."""
        self._simulate_transaction(trans_type='RFND')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(
            msg,
            "test_user_1_: Calling 'disable_member' in niteoweb.ipn.core.",
        )

    def test_CGBK(self):
        """Test CGBK Transaction Type."""
        self._simulate_transaction(trans_type='CGBK')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(
            msg,
            "test_user_1_: Calling 'disable_member' in niteoweb.ipn.core.",
        )

    def test_INSF(self):
        """Test INSF Transaction Type."""
        self._simulate_transaction(trans_type='INSF')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(
            msg,
            "test_user_1_: Calling 'disable_member' in niteoweb.ipn.core.",
        )

    def test_CANCEL_REBILL(self):
        """Test CANCEL-REBILL Transaction Type."""
        self._simulate_transaction(trans_type='CANCEL-REBILL')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(
            msg,
            "test_user_1_: Calling 'disable_member' in niteoweb.ipn.core.",
        )

    def test_UNCANCEL_REBILL(self):
        """Test UNCANCEL-REBILL Transaction Type."""
        self._simulate_transaction(trans_type='UNCANCEL-REBILL')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(
            msg,
            "test_user_1_: Calling 'enable_member' in niteoweb.ipn.core.",
        )


class TestUtils(IntegrationTestCase):
    """Test utility methods in @@jvzoo."""

    def setUp(self):
        """Prepare testing environment."""
        self.portal = self.layer['portal']
        self.view = self.portal.restrictedTraverse('jvzoo')

    def test_verify_POST(self):
        """Test POST verification process."""
        params = dict(
            secretkey='secret',
            ccustname='fullname',
            cverify='38CFCDED',
        )
        self.view._verify_POST(params)
        self.assertTrue(True)

    def test_parse_POST(self):
        """Test that POST parameters are correctly mirrored into member
        fields.
        """
        post_params = dict(
            ccustname='fullname',
            ccustemail='email',
            cproditem='product_id',
            ctransaffiliate='affiliate',
            ctransaction='SALE',
        )

        expected = dict(
            fullname=u'fullname',
            email='email',
            product_id='product_id',
            affiliate='affiliate',
            trans_type='SALE',
        )

        result = self.view._parse_POST(post_params)
        self.assertEqual(result, expected)
