# Server-side errors #
class YetiApiInternalErrorException(Exception):
    """ A general exception that covers all errors caused by the server """


class OutlookApiErrorException(YetiApiInternalErrorException):
    """ Raised when an error is encountered when communicating with Outlook Api """


class GmailApiErrorException(YetiApiInternalErrorException):
    """ Raised when an error is encountered when communicating with Gmail Api """


class DatabaseAccessErrorException(YetiApiInternalErrorException):
    """ Raised when an error is encountered when communicating with databases """


class YetiAuthInvalidTokenException(YetiApiInternalErrorException):
    """ Raised when the Yeti auth service finds that an access token is invalid """


class YetiAuthTokenExpiredException(YetiAuthInvalidTokenException):
    """ Raised when the Yeti auth service finds that an access token has been expired and should be refreshed """


# Item not found in DB #
class DatabaseItemNotFoundError(Exception):
    """ Raised when an error is encountered when the required data is not present in the DB """


# More than one item or no item is found in DB: illegal state #
class DatabaseItemNotExistentOrUniqueError(Exception):
    """ Raised when more than one item or no item is found in DB: illegal state """


# Client-side errors #
class YetiApiClientErrorException(Exception):
    """ A general exception that covers all errors caused by the client request """


class YetiApiBadEventBodyException(YetiApiClientErrorException):
    """ Raised if the Lambda handler cannot parse the received event """


class YetiPaymentAlreadyAppliedException(YetiApiClientErrorException):
    """ Raised if the payment is already applied to an order but is tried to apply to another """


class YetiInvalidPaymentEmailException(Exception):
    """ Raised when the payment email cannot be parsed, or is irrelevant to ski tickets, etc. """


class EmailTransformationErrorException(YetiInvalidPaymentEmailException):
    """ Raised when an error is encountered when transforming an email """
