# -*- coding: utf-8 -*-


class HolviException(Exception):
    def __init__(self, id_, message):
        self.message = message
        self.id = id_

    def __str__(self):
        return "{0!s} {1}".format(self.id, self.message)


class HolviDataItemException(HolviException):
    pass


class HolviVaultException(HolviException):
    pass


class HolviClusterException(HolviException):
    pass


class HolviNameException(HolviException):
    pass


class HolviCryptException(HolviException):
    pass


class HolviUnknownException(HolviException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

    def __str__(self):
        return Exception.__str__(self)


class HolviURLException(HolviException):
    pass


class HolviClientException(HolviException):
    pass


class HolviAuthException(HolviException):
    pass


class HolviAPIException(HolviException):
    pass


class HolviProtocolException(HolviException):
    pass


class ClientException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "{0!s}".format(self.message)


class ClientMetaException(ClientException):
    pass


class ClientKeyFileException(ClientException):
    pass
