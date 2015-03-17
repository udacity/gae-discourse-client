"""Gateway for accessing the Discourse API (for forums)"""

import json
import re
from urllib import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import categories as categories_module
import groups as groups_module
import users as users_module


class Error(Exception):
    pass


class DiscourseAPIClient(object):
    """An API client for interacting with Discourse"""

    def __init__(self, discourse_url, api_key, api_username='system'):
        self._discourse_url = discourse_url
        self._api_key = api_key
        self._api_username = api_username

    @ndb.tasklet
    def getRequest(self, req_string, params=None, payload=None):
        response = yield self._sendDiscourseRequest(
            req_string, params, payload, 'GET')
        raise ndb.Return(response)

    @ndb.tasklet
    def putRequest(self, req_string, params=None, payload=None):
        response = yield self._sendDiscourseRequest(
            req_string, params, payload, 'PUT')
        raise ndb.Return(response)

    @ndb.tasklet
    def postRequest(self, req_string, params=None, payload=None):
        response = yield self._sendDiscourseRequest(
            req_string, params, payload, 'POST')
        raise ndb.Return(response)

    @ndb.tasklet
    def deleteRequest(self, req_string, params=None, payload=None):
        response = yield self._sendDiscourseRequest(
            req_string, params, payload, 'DELETE')
        raise ndb.Return(response)

    @ndb.tasklet
    def _sendDiscourseRequest(self, req_string, params, payload, method):
        if payload is None:
            payload = {}
        if params is None:
            params = {}

        if method == 'GET' or method == 'DELETE':
            params.update({
                'api_key': self._api_key,
                'api_username': self._api_username
            })
        else:
            payload.update({
                'api_key': self._api_key,
                'api_username': self._api_username
            })

        url = self._discourse_url + req_string

        if params:
            url += '?' + urlencode(params)

        response = yield ndb.get_context().urlfetch(
            url=url, payload=urlencode(payload), method=method,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        if response.status_code != 200:
            raise Error(
                "%s request to %s returned a code of %d" %
                (method, req_string, response.status_code)
            )

        raise ndb.Return(json.loads(response.content))


users = None
groups = None
categories = None


def initClient(discourse_url, api_key, api_username):
    _api_client = DiscourseAPIClient(discourse_url, api_key, api_username)

    global users, groups, categories

    users = users_module.UserClient(_api_client)
    groups = groups_module.GroupClient(_api_client, users)
    categories = categories_module.CategoryClient(_api_client)
