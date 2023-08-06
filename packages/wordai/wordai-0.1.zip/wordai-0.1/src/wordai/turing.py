#!/usr/bin/python
# -*- coding: utf-8 -*-

from wordai import WordAi


class TuringWordAi(WordAi):
    """A class representing the WordAI Turing API
    (http://wordai.com/api.php?type=turing).
    All articles must be in UTF-8 encoding!
    """

    """URL for invoking the API"""
    URL = 'http://wordai.com/users/turing-api.php'

    DEFAULT_PARAMS = {
        's': "",
        'quality': "Regular",
        'email': "",
        'hash': "",
        'output': "json",
    }
