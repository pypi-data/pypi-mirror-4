# -*- coding: utf-8 -*-
__license__ = """
Copyright 2010-2012 elfCLOUD / elfcloud.fi – SCIS Secure Cloud Infrastructure Services

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


class ECException(Exception):
    def __init__(self, id_, message):
        self.message = message
        self.id = id_

    def __str__(self):
        return "{0!s} {1}".format(self.id, self.message)


class ECDataItemException(ECException):
    pass


class ECVaultException(ECException):
    pass


class ECClusterException(ECException):
    pass


class ECNameException(ECException):
    pass


class ECCryptException(ECException):
    pass


class ECUnknownException(ECException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

    def __str__(self):
        return Exception.__str__(self)


class ECURLException(ECException):
    pass


class ECClientException(ECException):
    pass


class ECAuthException(ECException):
    pass


class ECAPIException(ECException):
    pass


class ECProtocolException(ECException):
    pass

class ECEntityNameException(ECException):
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
