# Server-side errors #
class YetiApiInternalErrorException(Exception):
    """ A general exception that covers all errors caused by the server """


class OutlookApiErrorException(YetiApiInternalErrorException):
    """ Raised when an error is encountered when communicating with Outlook Api """


class GmailApiErrorException(YetiApiInternalErrorException):
    """ Raised when an error is encountered when communicating with Gmail Api """


class DatabaseAccessErrorException(YetiApiInternalErrorException):
    """ Raised when an error is encountered when communicating with databases """


class EmailTransformationErrorException(YetiApiInternalErrorException):
    """ Raised when an error is encountered when transforming an email """


class YetiAuthInvalidTokenException(YetiApiInternalErrorException):
    """ Raised when the Yeti auth service finds that an access token is invalid """


class YetiAuthTokenExpiredException(YetiAuthInvalidTokenException):
    """ Raised when the Yeti auth service finds that an access token has been expired and should be refreshed """


# Item not found in DB #
class DatabaseItemNotFoundError(Exception):
    """ Raised when an error is encountered when the required data is not present in the DB """


# Client-side errors #
class YetiApiClientErrorException(Exception):
    """ A general exception that covers all errors caused by the client request """


class YetiApiBadEventBodyException(YetiApiClientErrorException):
    """ Raised if the Lambda handler cannot parse the received event """


class YetiInvalidPaymentEmailException(Exception):
    """ Raised when the payment email cannot be parsed, or is irrelevant to ski tickets, etc. """
