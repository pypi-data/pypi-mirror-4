# -*- coding: utf-8 -*-


class WordAiError(Exception):
    """Base class for exceptions in WordAi module."""
    def __init__(self, api_error_msg):
        self.api_error_msg = api_error_msg

    def __str__(self):
        if not self.api_error_msg:
            return "Exception occurred."
        else:
            return self.api_error_msg


class NetworkError(WordAiError):
    """Raised if there are network problems, like timeout."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class AuthenticationError(WordAiError):
    """Raised when authentication error occurs."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class InternalError(WordAiError):
    """Raised when unexpected error occurs on the
    API server when processing a request."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class SpinError(WordAiError):
    """Raised when spinning article."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class UnknownError(WordAiError):
    """Raised when API call results in an unrecognized error."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
