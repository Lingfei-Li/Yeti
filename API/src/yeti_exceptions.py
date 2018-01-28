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


class YetiApiClientErrorException(Exception):
    """ A general exception that covers all errors caused by the client request """


class YetiAuthTokenExpiredException(Exception):
    """ Raised when the Yeti auth service finds that an access token has been expired and should be refreshed """

