# -*- coding: utf-8 -*-

from exceptions import AuthenticationError
from exceptions import QuotaUsedError

import re
import urllib2
import urllib
import phpserialize


class Api(object):
    """ A class to use The Best Spinner api
        (get an account at http://snurl.com/the-best-spinner)
    """
    def __init__(self, username, password):
        self.url = 'http://thebestspinner.com/api.php'
        self.username = username
        self.password = password
        self.authenticated = False
        self.token = ''

    def _authenticate(self):
        """
        Gets and stores session identifier
        to be used for each subequent request
        """
        if self.authenticated:
            return

        data = (
            ('action', 'authenticate'),
            ('format', 'php'),
            ('username', self.username),
            ('password', self.password),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        php = con.read()
        result = phpserialize.loads(php)

        if result['success'] == 'true':
            self.authenticated = True
            self.token = result['session']
        else:
            raise AuthenticationError(self.username, self.password)

    def identifySynonyms(self, text, max_syns=3, phrases=()):
        """
        Calls the 'identitySynonyms' api function
        (counts towards api query quota).
        Returns spin-formatted text,
        identified synonyms are replaced.

        Args:
            text (str): The text to perform the synonym identification on
            (max 5,000 words).

        Kwargs:
            max_syns (int): The maximum number of
            synonyms to return for a word/phrase, default 3.
            phrases (tuple or list): Phrases/words in text
            that should not be altered and synonyms not sought.
        """
        if not self.authenticated:
            self._authenticate()

        text = self._replacePhrases(text, phrases)
        data = (
            ('action', 'identifySynonyms'),
            ('format', 'php'),
            ('session', self.token),
            ('text', text.encode('utf-8')),
            ('maxsyns', max_syns),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        php = con.read()

        result = phpserialize.loads(php)

        if result['success'] == 'true':
            output = result['output'].decode("utf-8")
            return self._replacePlaceholders(output, phrases)

        else:
            if self.apiQuota() <= 250:
                raise QuotaUsedError()
            else:
                raise Exception("identifySynonyms failed, reason unknown")

    def replaceEveryonesFavorites(
        self,
        text,
        max_syns=3,
        quality=3,
        phrases=()
    ):
        """
        Calls the 'replaceEveryonesFavorites' api function
        (counts towards api query quota).
        Returns spin-formatted text with 'everyone's favorites' replaced.

        Args:
            text (str): The text to perform the synonym identification on
            (max 5,000 words).

        Kwargs:
            max_syns (int): The maximum number of synonyms
            to return for a word/phrase, default 3.
            quality (int): 1 = Good, 2 = Better, 3 = Best.
            phrases (tuple or list): Phrases/words in text
            that should not be altered and synonyms not sought.
        """
        if not self.authenticated:
            self._authenticate()

        text = self._replacePhrases(text, phrases)

        data = (
            ('action', 'replaceEveryonesFavorites'),
            ('format', 'php'),
            ('session', self.token),
            ('text', text.encode('utf-8')),
            ('maxsyns', max_syns),
            ('quality', quality),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        php = con.read()
        result = phpserialize.loads(php)

        if result['success'] == 'true':
            output = result['output'].decode("utf-8")
            return self._replacePlaceholders(output, phrases)

        else:
            if self.apiQuota() <= 250:
                raise QuotaUsedError()
            else:
                raise Exception(
                    "replaceEveryonesFavorites failed, reason unknown"
                )

    def randomSpin(self, text, phrases=()):
        """
        Calls the 'randomSpin' api function, returns a spun version of
        the spin-formatted text provided.

        Args:
            text (str): Spin-formatted text to return
            a randomly spun version of (max 5,000 words).

        Kwargs:
            phrases (tuple or list): Phrases/words in text that
            should not be altered and synonyms not sought.
        """
        if not self.authenticated:
            self._authenticate()

        text = self._replacePhrases(text, phrases)
        data = (
            ('action', 'randomSpin'),
            ('format', 'php'),
            ('session', self.token),
            ('text', text.encode('utf-8')),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        php = con.read()
        result = phpserialize.loads(php)

        if result['success'] == 'true':
            output = result['output'].decode("utf-8")
            return self._replacePlaceholders(output, phrases)

        else:
            if self.apiQuota() <= 250:
                raise QuotaUsedError()
            else:
                raise Exception("randomSpin failed, reason unknown")

    def apiQueries(self):
        """
        Returns the number of api requests made today
        (the api has a limit of 250 per day).
        """
        if not self.authenticated:
            self._authenticate()

        data = (
            ('action', 'apiQueries'),
            ('format', 'php'),
            ('session', self.token),
        )
        con = urllib2.urlopen(self.url, urllib.urlencode(data))
        php = con.read()
        result = phpserialize.loads(php)

        if result['success'] == 'true':
            return int(result['output'])

        else:
            raise Exception("apiQueries failed, reason unknown")

    def _replacePhrases(self, text, phrases):
        """
        A utility method to replace words/phrases
        that shouldn't be identified as synonyms with a placeholder.
        @param text: Text in which to replace words/phrases.
        @param phrases: a tuple or list of phrases to replace
        (a phrase can be one or more words eg 'cat' and 'a dog')
        """
        for i, phrase in enumerate(phrases):
            for match in re.finditer(r'\b(%s)\b' % phrase, text):
                text = text[:match.start(1)] + '~%d~' % i + text[match.end(1):]

        return text

    def _replacePlaceholders(self, text, phrases):
        """
        A utility method to replace placeholders with the original
        words/phrases that were switched with _replacePhrases
        @param text: Text in which to unmark words/phrases.
        @param phrases: the same tuple or list that
                        was passed to _replacePhrases()
        """
        for i, phrase in enumerate(phrases):
            text = text.replace('~%d~' % i, phrases[i])

        return text
