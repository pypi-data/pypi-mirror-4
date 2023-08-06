class InvalidClient(Exception):
    """Client authentication failed (e.g., unknown client, no
    client authentication included, or unsupported
    authentication method).

    """

    def __init__(self, message=''):
        self.__message = message

    def __str__(self):
        return repr(self.__message)


class UnsupportedGrantType(Exception):
    """The authorization grant type is not supported by the
    authorization server.

    """

    def __init__(self, message=''):
        self.__message = message

    def __str__(self):
        return repr(self.__message)


class InvalidGrant(Exception):
    """The provided authorization grant (e.g., authorization
    code, resource owner credentials) or refresh token is
    invalid, expired, revoked, does not match the redirection
    URI used in the authorization request, or was issued to
    another client.

    """

    def __init__(self, message=''):
        self.__message = message

    def __str__(self):
        return repr(self.__message)
