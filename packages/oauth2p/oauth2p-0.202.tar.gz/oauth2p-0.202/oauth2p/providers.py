from oauth2p import utils
from oauth2p.exceptions import UnsupportedGrantType, InvalidClient, InvalidGrant


class Authorization(object):

    def __init__(self, storage, token_length=40, expire=3600):
        self.__storage = storage
        self.__token_length = token_length
        self.__expire = expire

    def get_access_token(self, grant_type, *args, **kwargs):
        return self.token_handlers.get(grant_type, self.__default_token_handler)(self, *args, **kwargs)

    @property
    def token_handlers(self):
        return self.__grant_type_handlers

    @property
    def token_length(self):
        return self.__token_length

    @property
    def storage(self):
        return self.__storage

    @property
    def token_type(self):
        return 'Bearer'

    @property
    def expire(self):
        return self.__expire

    def revoke(self, token, token_type, client_id=None):
        return self.storage.delete(token=token, token_type=token_type, client_id=client_id)

    def __default_token_handler(self, *args, **kwargs):
        raise UnsupportedGrantType()

    def __client_credentials(self, **kwargs):
        token = utils.generate_random_vschar(self.token_length)
        self.storage.save(token=token, token_type='access_token', client_id=None, data=kwargs, expire=self.expire)

        return {
            "access_token": token,
            "token_type": self.token_type,
            "expires_in": self.expire,
        }

    def __password(self, **kwargs):
        username = kwargs.pop('username', None)
        password = kwargs.pop('password', None)

        if not username or not password or not self.storage.is_valid_owner(username, password, **kwargs):
            raise InvalidClient()

        token = utils.generate_random_vschar(self.token_length)
        refresh_token = utils.generate_random_vschar(self.token_length)

        token_key = self.storage.save(token=token, token_type='access_token',
                                      client_id=None, data=kwargs, expire=self.expire)
        refresh_key = self.storage.save(token=refresh_token, token_type='refresh_token',
                                        client_id=None, data=kwargs, expire=None)
        return {
            "access_token": token,
            "token_type": self.token_type,
            "expires_in": self.expire,
            "refresh_token": refresh_token
        }

    def __refresh_token(self, **kwargs):
        client_id = kwargs.get('client_id', None)
        token_data = self.storage.get(kwargs.get('refresh_token', None), 'refresh_token', client_id)

        if not token_data:
            raise InvalidGrant()

        token = utils.generate_random_vschar(self.token_length)
        self.storage.save(token=token, token_type='access_token', client_id=None, data=kwargs, expire=self.expire)
        return {
            "access_token": token,
            "token_type": self.token_type,
            "expires_in": self.expire,
            "refresh_token": kwargs['refresh_token']
        }

    __grant_type_handlers = {
        'client_credentials': __client_credentials,
        'password': __password,
        'refresh_token': __refresh_token
    }


class Resource(object):
    def __init__(self, storage):
        self.__storage = storage

    @property
    def storage(self):
        return self.__storage

    def is_valid_token(self, token):
        return self.storage.get(token=token, token_type='access_token', client_id=None) is not None


class PersistentStorage(object):
    def is_valid_owner(self, username, password, **kwargs):
        raise NotImplementedError()

    def save(self, token, token_type, data, expire, client_id):
        raise NotImplementedError()

    def get(self, token, token_type, client_id):
        raise NotImplementedError()

    def delete(self, token, token_type, client_id):
        raise NotImplementedError()