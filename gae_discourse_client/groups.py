"""Gateway for accessing the Discourse API (for forums)"""

import json
import re
from urllib import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb


class Error(Exception):
    pass


class GroupClient(object):
    """An API client for interacting with Discourse for group-related actions"""

    def __init__(self, api_client, user_client):
        self._api_client = api_client
        self._user_client = user_client

    @ndb.tasklet
    def addUser(self, user_email, group_name):
        """Adds the given account to the Discourse group with the given name"""

        user = yield self._user_client.getByEmail(user_email)
        if not user:
            raise Error("Unable to find user with email %s" % user_email)

        group = yield self.getByName(group_name)
        if not group:
            raise Error("Group named %s not found" % group_name)

        payload = {
            'usernames': user['username']
        }

        result = yield self._api_client.putRequest(
            'admin/groups/%s/members.json' % group['id'], payload=payload
        )
        raise ndb.Return(result)

    @ndb.tasklet
    def removeUser(self, user_email, group_name):
        """Removes an account from a group"""

        user = yield self._user_client.getByEmail(user_email)
        if not user:
            raise Error("Unable to find user with email %s" % user_email)

        group = yield self.getByName(group_name)
        if not group:
            raise Error("Group named %s not found" % group_name)

        result = yield self._api_client.deleteRequest(
            'admin/groups/%s/members.json' % group['id'],
            params={'user_id': user['id']}
        )
        raise ndb.Return(result)

    @ndb.tasklet
    def create(self, group_name, strict=False, **kwargs):
        """Creates a group with the given name on Discourse"""

        group = yield self.getByName(group_name)
        if group:
            if not strict:
                raise ndb.Return(None)
            else:
                raise Error("Group named %s already exists!" % group_name)

        payload = {
            'name': group_name
        }

        for k, v in kwargs.iteritems():
            payload[k] = v

        response = yield self._api_client.postRequest('admin/groups', payload=payload)
        raise ndb.Return(response)

    @ndb.tasklet
    def delete(self, group_name, strict=False):
        group = yield self.getByName(group_name)
        if not group:
            if not strict:
                raise ndb.Return(None)
            else:
                raise Error("Could not find group with name %s" % group_name)

        response = yield self._api_client.deleteRequest('admin/groups/%s' % group['id'])
        raise ndb.Return(response)

    @ndb.tasklet
    def getByName(self, group_name):
        groups = yield self._api_client.getRequest('admin/groups.json')

        for group in groups:
            if group['name'] == group_name:
                raise ndb.Return(group)

        raise ndb.Return(None)
