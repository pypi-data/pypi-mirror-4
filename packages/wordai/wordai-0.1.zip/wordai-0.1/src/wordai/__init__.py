#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import md5
import re
import urllib
import urllib2
import socket

from wordai import exceptions as ex


class WordAi(object):
    """A class representing the WordAI API
    (http://wordai.com/api.php).
    All articles must be in UTF-8 encoding!
    """

    """URLs for invoking the API"""
    URL = None
    ACCOUNT_URL = 'http://wordai.com/users/account-api.php'

    TIMEOUT = 20

    DEFAULT_PARAMS = None

    def __init__(self, email, password):
        """Initializes the spin api object.

        :param email: login email address
        :type email: str
        :param password: login password (only hash is saved in object)
        :type password: str
        """
        self._email = email
        self._md5hash = md5.md5(md5.md5(password).hexdigest()[:15]).hexdigest()

    def _stripslashes(self, s):
        return re.sub(r'\\', '', s)

    def _send_request(self, url, text=None, params=None):
        """ Invoke Word Ai API with given parameters and return its response.

        :param params: parameters to pass along with the request
        :type params: dictionary

        :return: API's response
        :rtype: dict
        """
        if params is not None:
            for k, v in params.items():
                params[k] = v.encode("utf-8")
        else:
            params = {}

        params['email'] = self._email
        params['hash'] = self._md5hash

        if text is not None:
            textdata = text.encode('utf-8')
            params['s'] = self._stripslashes(textdata)

        try:
            response = urllib2.urlopen(
                url,
                data=urllib.urlencode(params),
                timeout=self.TIMEOUT
            )
        except socket.timeout as e:
            raise ex.NetworkError(str(e))

        result = response.read()

        try:
            json_data = json.loads(result)
        except ValueError as e:
            raise ex.InternalError(str(e))

        if json_data['status'] == "Success":
            return json_data
        elif json_data['status'] == "Failure":
            if json_data['error'].startswith("Error Authenticating."):
                raise ex.AuthenticationError(str(json_data['error']))
            else:
                raise ex.SpinError(json_data['error'])
        else:
            raise ex.UnknownError(result)

    def account_info(self):
        """Return account info.

        :return: account info
        :rtype: dict
        :Example: {u'Standard Limit': 2500000, u'Status': u'Success',
            u'Turing Limit': 150000, u'Standard Usage': 0, u'Turing Usage': 0}
        """
        return self._send_request(self.ACCOUNT_URL)

    def text_with_spintax(self, text, params=None):
        """ Return processed spun text with spintax.

        :param text: original text that needs to be changed
        :type text: string
        :param params: parameters to pass along with the request
        :type params: dictionary

        :return: processed text in spintax format
        :rtype: string
        """

        if not params:
            params = self.DEFAULT_PARAMS.copy()

        params['returnspin'] = 'false'

        return self._send_request(
            url=self.URL,
            text=text,
            params=params
        )['text']

    def unique_variation(self, text, params=None):
        """ Return a unique variation of the given text.

        :param text: original text that needs to be changed
        :type text: string
        :param params: parameters to pass along with the request
        :type params: dictionary

        :return: processed text
        :rtype: string
        """

        if not params:
            params = self.DEFAULT_PARAMS.copy()

        params['returnspin'] = 'true'

        return self._send_request(
            url=self.URL,
            text=text,
            params=params
        )['text']
