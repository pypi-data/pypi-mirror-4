# Copyright (c) 2012 <Jaume Devesa (jaumedevesa@gmail.com)>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""

gists.utils
~~~~~~~~~~~

This module provides utils class and functionallity such as
base64 encoding, 'requests' module encapsulation, result data model, etc...

"""

import json
import requests
import urllib2
import os
import literals
import ConfigParser


class Result(object):
    """ The :class: `Result <Result>`.

    This class is return type of all the methods in 'gists.actions' module.
    """
    def __init__(self):
        self.success = False
        self.data = None


class GithubFacade(object):
    """ :class: `GithubFacade <GithubFacade> executes all the calls to Github.

    Although it is a trivial class, it is useful to mock its behavior
    in tests and to encapsulate the 'requests' dependency
    """
    # Endpoints to gists' github API
    ENDPOINT_LIST = "https://api.github.com/users/%s/gists"
    ENDPOINT_GIST = "https://api.github.com/gists/%s"
    ENDPOINT_CREATE = "https://api.github.com/gists"
    ENDPOINT_AUTH = "https://api.github.com/authorizations"

    # Default content type
    APPLICATION_JSON = "application/json"

    def __init__(self, username=None, credential=None):
        """ Initializes the Github facade.

        :param username: The username used to connect to the API. Can
                be None if using the token based authentication.
        :param credential: The password (if username provided) or the
                token to be used to authenticate.
        """
        self.username = username
        self.credential = credential
        self.basic_auth = (username is not None)

    def request_list_of_gists(self, username):
        """ Call to get a list of gists for user.

        :param token: Github authentication token
        """
        # Set the URL
        url = self.ENDPOINT_LIST % (username)

        if self.basic_auth and self.credential:
            return requests.get(url, auth=(self.username, self.credential))
        else:
            params = {}
            if self.credential:
                # Set the authentication header only if the password is set
                params = {'access_token': self.credential}
            return requests.get(url, params=params)

    def request_gist(self, id_gist):
        """ Request a single Gist info.

        :param id_gist: identifier of the gist.
        """

        # Set the URL and send the request
        url = self.ENDPOINT_GIST % (id_gist)
        return requests.get(url)

    def create_gist(self, payload):
        """ Create a new gist.

        :param payload: the data of the message body. It contains description,
            whenever is public or private and, of course, file contents.
        """

        url = self.ENDPOINT_CREATE
        headers = {'Content-type': self.APPLICATION_JSON}
        data_json = json.dumps(payload, indent=2)

        if self.basic_auth:
            return requests.post(url, data=data_json, headers=headers,
                    auth=(self.username, self.credential))
        else:
            params = {'access_token': self.credential}
            return requests.post(url, data=data_json, headers=headers,
                    params=params)

    def update_gist(self, payload):
        """ Update an existent Gist via PATCH method.

        :param payload: the data of the message body. It contains description,
            whenever is public or private and, of course, file contents.
        """

        url = self.ENDPOINT_GIST % (payload.identifier)
        headers = {'Content-type': self.APPLICATION_JSON}
        data_json = json.dumps(payload, indent=2)

        if self.basic_auth:
            return requests.patch(url, data=data_json, headers=headers,
                    auth=(self.username, self.credential))
        else:
            params = {'access_token': self.credential}
            return requests.patch(url, data=data_json, headers=headers,
                    params=params)

    def delete_gist(self, id_gist):
        """ Delete an existent Gist.

        :param id_gist: identifier of the Gist to delete
        """
        url = self.ENDPOINT_GIST % (id_gist)
        if self.basic_auth:
            return requests.delete(url,
                    auth=(self.username, self.credential))
        else:
            params = {'access_token': self.credential}
            return requests.delete(url, params=params)

    def list_authorizations(self):
        """ List the authorizations for the given user. """
        return requests.get(self.ENDPOINT_AUTH,
                auth=(self.username, self.credential))

    def authorize(self, payload):
        """ Authorize the current app.

        :param payload: The data of the message body. It contains the
            authorization request information.
        """
        url = self.ENDPOINT_AUTH
        headers = {'Content-type': self.APPLICATION_JSON}
        data_json = json.dumps(payload, indent=2)
        return requests.post(url, data=data_json, headers=headers,
                auth=(self.username, self.credential))


class GistsConfigurer(object):
    """ The :class: `GistsConfigurer <GistsConfigurer>` is the module that
    sets and gets data from the configuration file '.gistsrc'
    """

    def __init__(self):
        """ Initializes the 'ConfigParser' instance.

        If it does not found the '~/.gistsrc' file from the current user,
        it creates it empty.
        """

        self.config = ConfigParser.ConfigParser()
        self.config_file_path = os.path.expanduser('~/.gistsrc')
        if os.path.exists(self.config_file_path):
            self.config.read(self.config_file_path)
        else:
            with open(self.config_file_path, 'w'):
                # just create the file
                pass

    def getConfigUser(self):
        """ Returns the user from the configuration file.

        If configuration instance con not load 'credentials' section,
        or user is not configured, it returns none.
        """

        if not self.config.has_section('credentials'):
            print literals.CONFIG_FILE_NOT_FOUND
            return None
        username = self.config.get('credentials', 'user')
        return username

    def setConfigUser(self, user):
        """ Sets the user into the configuration file. """

        if not self.config.has_section('credentials'):
            self.config.add_section('credentials')
        self.config.set('credentials', 'user', user)
        with open(self.config_file_path, 'w') as f:
            self.config.write(f)

    def getConfigToken(self):
        """ Returns the auth token from the configuration file.

        If configuration instance con not load 'credentials' section,
        or user is not configured, it returns none.
        """

        if not self.config.has_section('credentials'):
            print literals.CONFIG_FILE_NOT_FOUND
            return None
        username = self.config.get('credentials', 'token')
        return username

    def setConfigToken(self, token):
        """ Sets the auth token into the configuration file. """

        if not self.config.has_section('credentials'):
            self.config.add_section('credentials')
        self.config.set('credentials', 'token', token)
        with open(self.config_file_path, 'w') as f:
            self.config.write(f)


def download(url, destination_dir, file_name, file_size):
    """ Downloads a file.

    :param url: remote location of the file
    :param destination_dir: target directory where the file will be
        download
    :param file_name: name of the target file
    :param file_size: size of the file to download.
    """

    destination_path = os.path.join(destination_dir, file_name)
    print (literals.DOWNLOADING
            % (url, destination_path, file_size))

    # Open the remote url as a file, read it and write it in
    # target directory
    u = urllib2.urlopen(url)
    with open(destination_path, 'wb') as f:
        raw_file = u.read()
        f.write(raw_file)


def build_result(success, data, *args):
    """ Builds the :class: `Result <Result>` as return type.

    :param success: whenever it has finished succesfully or not
    :param data: data to print (Gist data or error data)
    :param *args: parametrized extra data.
    """

    # Not too much magic here
    result = Result()
    result.success = success
    if not args:
        result.data = data
    else:
        result.data = data % (args)
    return result
