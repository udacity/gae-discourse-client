"""Gateway for accessing the Discourse API (for forums)"""

import json
import re
from urllib import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb


class Error(Exception):
    pass


class UserClient(object):
    """An API client for interacting with Discourse for user-related actions"""

    def __init__(self, api_client):
        self._api_client = api_client

    # USER ACTIONS

    @ndb.tasklet
    def getByEmail(self, user_email):
        """Finds the Discourse user with the given email"""
        users = yield self._api_client.getRequest(
            'admin/users/list/active.json',
            params={'filter': user_email, 'show_emails': 'true'}
        )

        for user in users:
            if user['email'].lower() == user_email.lower():
                raise ndb.Return(user)

        raise ndb.Return(None)

    @ndb.tasklet
    def create(self, name, email, password, username, external_id=None):
        """Create a Discourse account

        This method takes user account info and returns the Discourse API response
        containing the user information for that user.
        """

        payload = {
            'username': username,
            'email': email,
            'name': name,
            'password': password,
            'active': 'true',
        }

        if external_id:
            payload['external_id'] = external_id

        response = yield self._api_client.postRequest('users/', payload=payload)
        raise ndb.Return(response)

    @ndb.tasklet
    def delete(self, email, strict=False):
        user = yield self.getByEmail(email)
        if user is None:
            if not strict:
                raise ndb.Return(None)
            else:
                raise Error("Could not find user with email %s" % email)

        response = yield self._api_client.deleteRequest('admin/users/%s.json' % user['id'])
        raise ndb.Return(response)
