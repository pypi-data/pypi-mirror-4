# -*- coding: utf-8 -*-

"""
    chrw.exceptions contains all the exceptions relating
    to the execution of the chr wrapper.
"""

class ChrwException(RuntimeError):
    """ Something went wrong when trying to work
        with the chr API.
    """

class RequestRateTooHigh(ChrwException):
    """ We're attempting to poll the API too
        darn frequently.
    """

class TimeIsBackToFront(ChrwException):
    """ We somehow traveled back in time,
        and there was no delorean.
    """

class RequestFailed(ChrwException):
    """ A POST request we sent didn't
        complete as 200 OK.
    """

class ApiDisabled(ChrwException):
    """ The chr API is disabled, so
        we can't do anything.
    """

class InvalidApiKey(ChrwException):
    """ We sent a request with an invalid
        API key.
    """

class PartialFormData(ChrwException):
    """ Something is missing from the
        form data.

        This might suggest an API update,
        and incompatibilities.
    """

class InvalidDataReturned(ChrwException):
    """ The reply we got didn't appear to
        be valid JSON data.
    """

class NonZeroReply(ChrwException):
    """ The reply returned a non-zero
        reply error number.
    """