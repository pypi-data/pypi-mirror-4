# -*- coding: utf-8 -*-


class TBSError(Exception):
    """Base class for exceptions in this module."""
    pass


class AuthenticationError(TBSError):
    """
    Raised when authentication error encountered
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return "Could not authenticate with username: "
        "{0} and password: {1}.".format(self.username, self.password)


class QuotaUsedError(TBSError):
    """
    Raised when API quota limit reached (250 queries per day)
    """
    def __str__(self):
        return "The Best Spinner API query limit has been"
        "reached for today (250 queries per day)."
