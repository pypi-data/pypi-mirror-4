# -*- coding: utf-8 -*-

from tbs import Api

import unittest2 as unittest
import mock


class TestApi(unittest.TestCase):

    def setUp(self):
        """Utility code shared among all tests."""

        self.tbs = Api('foo@bar.com', 'test_password')

    def test_init(self):
        """Test initialization of TheBestSpinner.

        TheBestSpinner is initialized on every test run and stored as self.tbs.
        We need to test for stored values if class was
        initialized correctly.
        """

        self.assertEquals(self.tbs.username, 'foo@bar.com')
        self.assertEquals(self.tbs.password, 'test_password')
        self.assertIsInstance(self.tbs, Api)

    @mock.patch('tbs.urllib2')
    def test_randomSpin_call(self, urllib2):
        """Test call of unique_variation() with default values."""

        # mock response from Api
        mocked_response = 'a:3:{s:7:"session";s:13:"bbbbbbbbbbbbb";'\
            's:6:"output";s:81:"This is actually '\
            'the text we would like to spin and rewrite & '\
            'also über felines!";s:7:"success";s:4:"true";}'
        urllib2.urlopen.return_value.read.return_value = mocked_response

        # test call
        self.assertEquals(
            self.tbs.randomSpin(
                u'{This is the|This is actually the|Here '
                u'is the|This can be the} {text|textual content|text '
                u'message|wording} {we want to|you want to|we would like '
                u'to|we should} {spin|rewrite|spin and rewrite|whirl} & '
                u'also über {cats|felines|pet cats|kittens and cats}!'
            ),
            u'This is actually the text we would like to spin and '
            u'rewrite & also über felines!',
        )

    @mock.patch('tbs.urllib2')
    def test_identifySynonyms_call(self, urllib2):
        """Test call of text_with_spintax_call() with default values."""

        # mock response from Api
        mocked_response = 'a:3:{s:7:"session";s:13:"aaaaaaaaaaaaa";'\
            's:6:"output";s:251:"{This is the|This is actually the|Here is '\
            'the|This can be the} '\
            '{text|textual content|text message|wording} '\
            '{we want to|you want to|we would like to|we should} '\
            '{spin|rewrite|spin and rewrite|whirl} & also über '\
            '{cats|felines|pet cats|kittens and '\
            'cats}!";s:7:"success";s:4:"true";}'
        urllib2.urlopen.return_value.read.return_value = mocked_response

        # test call
        self.assertEquals(
            self.tbs.identifySynonyms(
                u"This is the text we want to spin & also über cats!"
            ),
            u"{This is the|This is actually the|Here is the|This can be the} "
            u"{text|textual content|text message|wording} "
            u"{we want to|you want to|we would like to|we should} "
            u"{spin|rewrite|spin and rewrite|whirl} & also "
            u"über {cats|felines|pet cats|kittens and cats}!"
        )
