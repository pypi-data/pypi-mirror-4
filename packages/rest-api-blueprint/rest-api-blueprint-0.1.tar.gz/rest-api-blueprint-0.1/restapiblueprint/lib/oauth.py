"""2-legged oauth 1.0 utilities.

Simplify usage down to essentially two functions:

    1) sign
    2) verify

We do NOT include the body in the signature or create a body hash. Therefore
there is no oauth_body_hash parameter. This is because it is not part of the
specification and because it has a performance impact with large messages. We
trick the oauth2 library into not hashing the body by setting
is_form_encoded=True. See

    http://oauth.googlecode.com/svn/spec/ext/body_hash/1.0/oauth-bodyhash.html

Note that we also assume that the body does NOT contain any of the oauth
parameters. They must be in the Authorization HTTP header or in the URL.

See
    http://tools.ietf.org/html/rfc5849
    http://oauth.net

"""
import oauth2
import time
import urlparse


# Declared oauth2 Signature method (standard HMAC_SHA1).
SIGNATURE_METHOD = oauth2.SignatureMethod_HMAC_SHA1()


# A "server" to sign requests.
oauth_server = oauth2.Server()
oauth_server.add_signature_method(SIGNATURE_METHOD)


def verify(get_secret, url, method, headers):
    """Verify (2-legged) oauth request.

    The get_secret function should take a consumer key and return the consumer
    secret or raise a KeyError.

    The oauth parameters can be in the "Authorization" header (found in headers)
    or in the URL parameters.

    Return the consumer secret key if verified ok, otherwise returns None. This
    is because the Python caller is very likely to go on to check that the
    verified HTTP caller is allowed to perform the action.

    """
    # We will build a set of all parameters...
    parameters = {}

    # Merge in parameters from the header, if defined.
    if 'Authorization' in headers:
        auth_header = headers['Authorization']
        if auth_header[:6] == 'OAuth ':
            auth_header = auth_header[6:]
            try:
                # Get the parameters from the header.
                header_params = oauth2.Request._split_header(auth_header)
                parameters.update(header_params)
            except:
                raise ValueError(
                    'Unable to parse OAuth parameters from header.')

    # Merge in parameters from the URL.
    param_str = urlparse.urlparse(url)[4]
    url_params = oauth2.Request._split_url_string(param_str)
    parameters.update(url_params)

    # Make the oauth2.Consumer object (key and secret).
    try:
        key = parameters['oauth_consumer_key']
        secret = get_secret(key)
        consumer = oauth2.Consumer(key, secret)
    except KeyError:
        return None  # Missing consumer key or secret

    # Create the oauth Request.
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
    base_url = urlparse.urlunparse((scheme, netloc, path, None, None, None))
    req = oauth2.Request(method, base_url, parameters, is_form_encoded=True)

    # Verify signature.
    try:
        oauth_server.verify_request(req, consumer, None)
        return key
    except oauth2.Error:
        return None


def get_HMAC_SHA1_signature_as_url(key, secret, url, http_method):
    """Create a two legged oauth HMAC_SHA1 signature.

    The key and secret are oauth consumer pairs.

    The created oauth signature parameters are included in the returned URL.

    """
    return _sign(SIGNATURE_METHOD, key, secret, url, http_method).to_url()


def get_HMAC_SHA1_signature_as_header(key, secret, url, http_method):
    """Create a two legged oauth HMAC_SHA1 signature.

    The key and secret are oauth consumer pairs.

    The created oauth signature parameters are included in the returned headers
    object.

    """
    return _sign(SIGNATURE_METHOD, key, secret, url, http_method).to_header()


def _sign(signature_method, key, secret, url, http_method):
    """Sign and return details in an oauth2.Request object."""
    parameters = {}
    parameters.update({
        'oauth_version': "1.0",
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'oauth_consumer_key': key,
        'oauth_token': ''
    })
    consumer = oauth2.Consumer(key, secret)
    req = oauth2.Request(
        url=url, method=http_method, parameters=parameters,
        is_form_encoded=True)
    req.sign_request(signature_method, consumer, None)
    return req
