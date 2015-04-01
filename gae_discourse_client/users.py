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
        """Finds the Discourse user with the given email.

        Args:
          user_email: The email address of the user to find.

        Returns:
          A dictionary containing information about the user if the user is successfully found,
          None otherwise
        """
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
        """Create a Discourse account.

        Args:
          name: Full name of the user.
          email: Email address of the user. This must be distinct from any other registered users
            on the site.
          password: Password of the user.
          username: Discourse username of the user. Must also be distinct from any other
            registered users.
          external_id: External ID for single sign-on, if it exists. This must be unique to your
            application (for more information on single sign-on, see
            https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045).

        Returns:
          A dictionary with the key 'success' set to True or False, depending on the outcome.
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
        """Delete a Discourse account.

        Args:
          email: Email address of the user to be deleted.
          strict: Whether to ensure that a user was actually deleted. If False, and the user does
            not exist, an error will be raised.

        Returns:
          A dictionary with the key 'deleted' set to True if the user is deleted, or None if the
            user does not exist and `strict` is False.

        Raises:
          Error: If `strict` is True and the user does not exist.
        """
        user = yield self.getByEmail(email)
        if user is None:
            if not strict:
                raise ndb.Return(None)
            else:
                raise Error("Could not find user with email %s" % email)

        response = yield self._api_client.deleteRequest('admin/users/%s.json' % user['id'])
        raise ndb.Return(response)
