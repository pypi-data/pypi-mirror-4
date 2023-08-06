# -*- coding: utf-8 -*-

from wordai import WordAi
from wordai import exceptions as ex
from wordai.regular import RegularWordAi
from wordai.turing import TuringWordAi

import json
import md5
import mock
import unittest2 as unittest
import socket


class TestApi(unittest.TestCase):

    def setUp(self):
        """Utility code shared among all tests.
        We test only RegularWordAi because TuringWordAi
        has the same parent class."""
        self.wai = RegularWordAi('foo@bar.com', 'password')

    def test_init(self):
        """Test initialization of WordAi.

        WordAi is initialized on every test run and stored as self.wai.
        We need to test for stored values if class was
        initialized correctly.
        """
        self.assertEquals(self.wai._email, 'foo@bar.com')
        self.assertEquals(
            self.wai._md5hash,
            md5.md5(md5.md5("password").hexdigest()[:15]).hexdigest()
        )
        self.assertIsInstance(self.wai, WordAi)

    def test_regular_url(self):
        """Test Regular API URL in RegularWordAi"""
        self.assertEquals(
            RegularWordAi.URL,
            "http://wordai.com/users/regular-api.php"
        )

    def test_turing_url(self):
        """Test Turing API URL in TuringWordAi"""
        self.assertEquals(
            TuringWordAi.URL,
            "http://wordai.com/users/turing-api.php"
        )

    def test_regular_params(self):
        """Test Regular-specific default parameters in RegularWordAi"""
        self.assertEquals(
            RegularWordAi.DEFAULT_PARAMS["quality"],
            "50"
        )

    def test_turing_params(self):
        """Test Turing-specific default parameters in TuringWordAi"""
        self.assertEquals(
            TuringWordAi.DEFAULT_PARAMS["quality"],
            "Regular"
        )

    @mock.patch('wordai.urllib2')
    def test_unique_variation_default_call(self, urllib2):
        """Test call of unique_variation() with default values."""
        # mock response from WordAi
        mocked_response = json.dumps({
            "uniqueness": 40,
            "status": "Success",
            "text": "Some evaluation text whič is fü.\n"
        })
        urllib2.urlopen.return_value.read.return_value = mocked_response

        # test call
        self.assertEquals(
            self.wai.unique_variation(u"Some test text whič is fü."),
            u"Some evaluation text whič is fü.\n",
        )

    @mock.patch('wordai.urllib2')
    def test_spintax_default_call(self, urllib2):
        """Test call of unique_variation() with default values."""
        # mock response from WordAi
        mocked_response = json.dumps({
            "uniqueness": 40,
            "status": "Success",
            "text": "Some {test|evaluation} text whič is fü.\n"
        })
        urllib2.urlopen.return_value.read.return_value = mocked_response

        # test call
        self.assertEquals(
            self.wai.text_with_spintax(u"Some test text whič is fü."),
            u"Some {test|evaluation} text whič is fü.\n",
        )

    @mock.patch('wordai.urllib2')
    def test_exception_timeout(self, mocked_urllib2):
        """Test timeout error."""
        # set side effect
        mocked_urllib2.urlopen.side_effect = socket.timeout("timeout foo")

        # test call
        self.assertRaises(
            ex.NetworkError,
            self.wai.unique_variation,
            u"Some test text whič is fü."
        )

    @mock.patch('wordai.urllib2')
    def test_exception_json(self, urllib2):
        """Test json exception."""
        # mock response from WordAi
        mocked_response = "invalid json schema"
        urllib2.urlopen.return_value.read.return_value = mocked_response

        # test call
        self.assertRaises(
            ex.InternalError,
            self.wai.unique_variation,
            u"blah"
        )

    @mock.patch('wordai.urllib2')
    def test_exception_failures(self, urllib2):
        """Test failure exceptions."""
        # mock response from WordAi
        mocked_response = json.dumps({
            "status": "Failure",
            "error": "Error Authenticating. fooooooooo"
        })
        urllib2.urlopen.return_value.read.return_value = mocked_response

        # test call
        self.assertRaises(
            ex.AuthenticationError,
            self.wai.unique_variation,
            u"blah"
        )

        mocked_response = json.dumps({
            "status": "Failure",
            "error": ("Error: You cannot process "
                      "articles longer than 10,000 words")
        })
        urllib2.urlopen.return_value.read.return_value = mocked_response

        # test call
        self.assertRaises(
            ex.SpinError,
            self.wai.unique_variation,
            u"blah"
        )

    @mock.patch('wordai.urllib2')
    def test_exception_unknown(self, urllib2):
        """Test failure exceptions."""
        # mock response from WordAi
        mocked_response = json.dumps({
            "status": "Failureeee",
            "error": "Some Error"
        })
        urllib2.urlopen.return_value.read.return_value = mocked_response

        # test call
        self.assertRaises(
            ex.UnknownError,
            self.wai.unique_variation,
            u"blah"
        )
