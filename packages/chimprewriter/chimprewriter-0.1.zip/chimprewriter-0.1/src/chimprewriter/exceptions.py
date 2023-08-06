# -*- coding: utf-8 -*-


class ChimpRewriterError(Exception):
    """Base class for exceptions in ChimpRewriter module."""
    def __init__(self, api_error_msg):
        #api_error_msg respresents raw error string as returned by API server
        super(ChimpRewriterError, self).__init__()
        self.api_errors = tuple(api_error_msg.split('|'))

    def __str__(self):
        if not self.api_errors:
            return "Exception occurred."
        elif len(self.api_errors) == 1:
            return self.api_errors[0]
        else:
            return "Multiple errors, see api_erros attribute for details."


class WrongParameterName(ChimpRewriterError):
    """Raised on unsuppported parameter name."""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return u"Parameter '{}' does not exist.".format(self.name)


class WrongParameterVal(ChimpRewriterError):
    """Raised on invalid parameter value."""
    def __init__(self, name, val):
        self.name = name
        self.val = val

    def __str__(self):
        return u"Parameter '{}' has a wrong value: '{}'".format(self.name, self.val)


class NetworkError(ChimpRewriterError):
    """Raised if there are network problems, like timeout."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class AuthenticationError(ChimpRewriterError):
    """Raised when authentication error occurs."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class QuotaLimitError(ChimpRewriterError):
    """Raised when API quota limit is reached."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class InternalError(ChimpRewriterError):
    """Raised when unexpected error occurs on the API server when processing a request."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ArticleError(ChimpRewriterError):
    """Raised when spinning article."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class UnknownError(ChimpRewriterError):
    """Raised when API call results in an unrecognized error."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
