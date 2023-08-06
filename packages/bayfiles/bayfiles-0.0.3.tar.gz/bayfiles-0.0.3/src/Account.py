#!/usr/bin/env python
# coding:utf-8
#
import requests
import sys


class Account(object):
    """
    Represent an account on the site bayfiles.com.

    Keywords arguments:
    username -- a string which is the username of the account
    password -- a string which is the password of the account
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.__login()

    def __login(self):
        """Authenticate and receive a session identifier."""
        url = BASE_URL + '/account/login/{0}/{1}'.format(self.username,
                                                         self.password)
        try:
            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()

            if json['error'] == u'':
                self.session = json['session']
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])

    def logout(self):
        """Delete the session related to the account on bayfiles.com."""
        url = BASE_URL + '/account/logout'
        url += '?session={0}'.format(self.session)

        try:
            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()
            if json['error'] == u'':
                self.session = None
                return
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])

    def info(self):
        """Return a dictionnary with information about the account."""
        url = BASE_URL + '/account/info'
        url += '?session={0}'.format(self.session)

        try:
            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()

            if json['error'] == u'':
                return json
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])

    def edit(self, key, value):
        """Not yet implemented"""
        raise NotImplementedError

    def files(self):
        """Return a dictionnary with the files belonging to the account."""
        url = BASE_URL + '/account/files'
        url += '?session={0}'.format(self.session)

        try:
            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()

            if json['error'] == u'':
                return json
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])
