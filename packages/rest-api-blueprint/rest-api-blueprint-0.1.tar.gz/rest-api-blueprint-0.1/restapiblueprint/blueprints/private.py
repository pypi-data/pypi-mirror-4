from flask import Blueprint, request
from restapiblueprint.lib import (
    http_method_dispatcher, make_ok, make_error, check, oauth)


blueprint = Blueprint(__name__, __name__)


def dumb_get_consumer_secret(key):
    """Return secret for given key or raise KeyError."""
    key_to_secret = {'akey': 'asecret'}
    return key_to_secret[key]


def dumb_check_have_capability(key, capabilities):
    """Return True if key has one of the given capabilities."""
    key_to_capabilities = {'akey': ['something']}
    capabilities_for_key = key_to_capabilities.get(key, [])
    for capability in capabilities_for_key:
        if capability in capabilities:
            return True
    return False


def access(*capabilities):
    """Return a function to check authentication and authorisation."""
    capabilities = set(capabilities)

    def check_access_with_capabilities(*args):
        key = oauth.verify(
            dumb_get_consumer_secret,
            request.url, request.method, request.headers)
        if key is None:
            return make_error(
                'Failed to authenticate', 401,
                additional_headers={'WWW-Authenticate': 'OAuth'})
        else:
            if not dumb_check_have_capability(key, capabilities):
                return make_error('Insufficient privileges to access', 403)
    return check_access_with_capabilities


@blueprint.route('', methods=['GET', 'POST'])
@http_method_dispatcher
class Private(object):

    @check(access('something', 'somethingelse'))
    def get(self):
        return make_ok()

    @check(access())
    def post(self):
        return make_ok()
