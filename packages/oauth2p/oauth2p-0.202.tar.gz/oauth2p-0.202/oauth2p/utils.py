import random
import string

UNICODE_ASCII_CHARACTERS = (string.ascii_letters.decode('ascii') +
                            string.digits.decode('ascii'))


def generate_random_vschar(length, ascii_characters=UNICODE_ASCII_CHARACTERS):
    """Returns random VSCHAR(%20 - 7E) as per RFC 6749 OAuth 2.0 October 2012
    Appendix A.  Augmented Backus-Naur Form (ABNF) Syntax.

    """
    return ''.join([random.choice(ascii_characters) for x in xrange(length)])


def generate_token_key(token, *args):
    """Returns token key for persistant storage.

    Keyword arguments:
    * token: token
    * type: token type (access_token, refresh_token)

    """
    return 'oauth2.' + '.'.join(str(arg) for arg in args if arg) + ':' + token
