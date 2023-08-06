#!/usr/bin/python
# -*- coding: utf-8 -*-

from wordai import WordAi


class RegularWordAi(WordAi):
    """A class representing the WordAI Regular API
    (http://wordai.com/api.php?type=regular).
    All articles must be in UTF-8 encoding!
    """

    """URL for invoking the API"""
    URL = 'http://wordai.com/users/regular-api.php'

    DEFAULT_PARAMS = {
        's': "",
        'quality': "50",
        'email': "",
        'hash': "",
        'output': "json",
    }
