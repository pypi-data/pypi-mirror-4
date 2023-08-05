# -*- coding: utf-8 -*-
import cookielib
import urllib2
import json

from exceptions import HolviUnknownException, HolviDataItemException
import elfcloud.exceptions as exceptions


class Connection(object):
    """Connection provides methods for communicating with elfCLOUD.fi server

    """
    __API_VERSION__ = "1.1"

    def __init__(self, server_url):
        """Initializer for Connection

        :param server_url: Server used for requests

        """
        self._server_url = server_url
        self._cookies = cookielib.CookieJar()
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookies))
        self._is_authed = False

    def auth(self, username, auth_data, auth_method, apikey):
        """Authenticates connection with given credentials

        :param username: Username used for authentication
        :param auth_data: Password used for authentication
        :param auth_method: Authentication method to be used
        :param apikey: Client's API-key

        """
        method = "auth"
        params = {
                    "username": username,
                    "auth_data": auth_data,
                    "auth_method": auth_method,
                    "apikey": apikey
                }
        self.make_request(method, params)
        self._is_authed = True

    def make_request(self, method, params):
        """Sends request to elfCLOUD.fi server with given method and parameters

        :param method: Operation to be performed on server
        :param params: Parameters for given method

        Sends a request to elfCLOUD.fi server and returns the result if the operation
        was succesful.

        """
        url = self._server_url + self.__API_VERSION__ + "/json"
        json_request = {
                "method": method,
                "params": params
                }

        post_data = json.JSONEncoder().encode(json_request)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        request = urllib2.Request(url, post_data, headers)
        response = self._opener.open(request).read()

        try:
            response = json.JSONDecoder().decode(response)
        except Exception as e:
            raise e

        if 'result' in response:
            return response['result']
        else:
            self._handle_exception(response)

    def make_transaction(self, headers, url_suffix, data=None):
        """Creates a transaction (download / upload) to elfCLOUD.fi server.

        :param headers: Headers to be added to the request
        :param url_suffix: '/store', '/fetch' depending on the direction of the transaction
        :param data: Data chunk to be added to request when POSTing data

        Sends the request with given headers to elfCLOUD.fi server.
        """
        url = self._server_url + self.__API_VERSION__ + url_suffix
        request = urllib2.Request(url)
        self._cookies.add_cookie_header(request)
        for key in headers:
            request.add_header(key, headers[key])
        request.data = data
        response = urllib2.urlopen(request)

        result = response.headers.get('X-HOLVI-RESULT')
        if result == 'OK':
            return response
        else:
            err_type, err_id, err_message = result.split(' ', 2)  # Format is 'ERROR: Err# ErrMessage'
            raise HolviDataItemException(err_id, err_message)

    def _handle_exception(self, response):
        """Handles the exceptions in request responses

        :param response: The response to be parsed for exceptions

        Parses the exception from response and raises correct exception.
        """
        exception = response.get('error')
        if not exception:
            raise HolviUnknownException()

        message = exception.get('message')
        code = exception.get('code')
        data = exception.get('data')

        if type(data) in [unicode, str] and hasattr(exceptions, data):
            raise getattr(exceptions, data)(code, message)
        else:
            raise HolviUnknownException("Unknown exception")
