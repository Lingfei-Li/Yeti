class YetiApiInternalErrorException(Exception):
    """ A general exception that covers all errors caused by the server """


class YetiApiClientErrorException(Exception):
    """ A general exception that covers all errors caused by the client request """


class YetiAuthTokenExpiredException(Exception):
    """ An exception indicating that the required access token has been expired and should be refreshed """

